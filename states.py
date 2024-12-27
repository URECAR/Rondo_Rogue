import pygame
from properties import *
from tile import Tile
from database import *
import random
from ui import ConfirmationDialog
from support import MessageDialog
class State:
    def __init__(self, map_action):
        self.map_action = map_action
        self.level = map_action.level
        self.cursor = map_action.level.cursor
        self.substate = None
    def __str__(self):
        # 현재 클래스명에서 'State'를 제거한 뒤 반환
        return self.__class__.__name__.replace('_State', '').lower()
    def __eq__(self, other):
        if isinstance(other, str):
            return str(self) == other
        return False
    def enter(self):
        pass
    def exit(self):
        pass
    def update(self):
        pass
class InitState(State):
    def update(self):
        for battler in self.level.battler_sprites:
            if battler.team != self.map_action.current_phase:
                battler.inactive = True
            self.map_action.apply_passive_skills(battler)
            battler.Cur_HP = int(battler.stats['Max_HP'])
            battler.Cur_MP = int(battler.stats['Max_MP'])
            self.map_action.recalculate_stats(battler,update_only=True)
        self.map_action.current_phase = 'Enemy'
        self.map_action.change_state("phase_change")
        self.map_action.sound_manager.play_bgm(**SOUND_PROPERTIES['ALLY_PHASE'])
class Explore_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
    def enter(self):
        if not hasattr(self, 'event_triggered') and self.map_action.current_phase == 'Ally':
            self.event_triggered = True
            Event1 = ["첫번째 이벤트입니다.", "메세지입니다."]
            print("!")
            return ('event', Event1, 'explore')
        if self.map_action.current_phase == 'Ally':
            self.cursor.move_lock = False
            self.cursor.SW_select = False
            self.cursor.selected = False
            self.cursor.select_lock = False
            for sprite in self.level.selectable_sprites:
                sprite.selected = False
            self.map_action.highlight_tiles_set(None,'Clear')
    def update(self):
        if self.map_action.current_phase == 'Ally':
            if self.cursor.SW_select and self.cursor.move_lock == False:
                self.cursor.move_lock = True
                # selectable 안엔 선택가능한 타일 스프라이트랑 배틀러 스트라이트가 존재함.
                for sprite in self.level.selectable_sprites:
                    if sprite in self.level.battler_sprites:
                        if sprite.pos == self.cursor.pos:
                            sprite.selected = True
                            self.map_action.selected_battler = sprite
                            self.map_action.input_manager.reset_mouse_state()
                            return 'player_control'
                        
                    elif sprite.sprite_type == 'Tile':
                        if [sprite.rect.x, sprite.rect.y] == self.cursor.pos * TILESIZE:
                            return 'look_object'
            elif not self.cursor.SW_select:
                self.cursor.move_lock = False
        elif self.map_action.current_phase == 'Enemy':
            self.level.cursor.move_lock = True
            actable_enemies = [battler for battler in self.level.battler_sprites if battler.team == 'Enemy' and not battler.inactive]
            if actable_enemies and not self.map_action.selected_battler:
                self.map_action.selected_battler = actable_enemies[0]
                self.level.visible_sprites.focus_on_target(self.map_action.selected_battler,cursor_obj=self.level.cursor)
                self.map_action.update_time = pygame.time.get_ticks() + 500
                self.substate = 'Enemy_wait'
                return
            elif self.substate == 'Enemy_wait' and self.map_action.update_time < pygame.time.get_ticks():
                self.substate = None
                return self.map_action.AI.execute()
class Look_Object_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
    def enter(self):
        self.cursor.move_lock = True
        self.level.focus_on_target(self.cursor.pos)
    def exit(self):
        self.cursor.move_lock = False
        self.cursor.SW_select = False
    def update(self):
        if self.map_action.input_manager.is_just_pressed('Cancel'):
            return 'explore'
class Player_Control_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
    def enter(self):
        self.cursor.move_lock = False
        self.map_action.cur_moves = self.map_action.selected_battler.stats['Mov']
        self.map_action.level.visible_sprites.focus_on_target(self.map_action.selected_battler)
        self.map_action.check_movable_from_pos(self.map_action.selected_battler.pos, self.map_action.cur_moves, show=True)
    def exit(self):
        self.cursor.move_lock = True
        self.cursor.SW_select = False
        self.map_action.highlight_tiles_set(None, 'Clear')
        if self.map_action.current_dialog:
            del self.map_action.current_dialog
            self.map_action.current_dialog = None
    def update(self):

        cursor_pos = self.cursor.pos * TILESIZE
        cursor_tile_x, cursor_tile_y = map(int, self.cursor.pos)
        
        if self.map_action.current_dialog:
            self.map_action.current_dialog.draw()
            self.cursor.move_lock = True  # 커서 이동 잠금
            result = self.map_action.current_dialog.handle_input(self.map_action.input_manager)
            if result is not None:
                if result:  # "예" 선택
                    self.map_action.current_dialog = None
                    return 'player_moving'
                else:
                    self.map_action.current_dialog = None
                    self.cursor.move_lock = False  # 커서 이동 잠금 해제
            return
        if self.cursor.is_dragging and self.cursor.last_drag_pos and not self.map_action.selected_battler.inactive:
            # 이동 비용 계산
            move_cost = int(self.level.level_data["moves"][cursor_tile_x][cursor_tile_y])
            
            # 이동 가능한 경우에만 처리
            if move_cost != -1 and move_cost <= self.map_action.cur_moves:
                last_pos = self.map_action.move_roots[-1][0].pos if self.map_action.move_roots else self.map_action.selected_battler.pos
                
                # 인접한 타일인지 확인
                is_adjacent = (abs(cursor_tile_x - last_pos.x) == 1 and cursor_tile_y == last_pos.y) or (abs(cursor_tile_y - last_pos.y) == 1 and cursor_tile_x == last_pos.x)
                
                if is_adjacent:
                    self.map_action.move_roots.append([Tile((cursor_pos[0], cursor_pos[1]),[self.map_action.visible_sprites, self.map_action.obstacle_sprites],'move_root'),move_cost])
                    self.map_action.cur_moves -= move_cost
                    self.map_action.update_path_tiles()
                    self.map_action.check_movable_from_pos(pygame.math.Vector2(cursor_pos) // TILESIZE, self.map_action.cur_moves, show=True)

        if self.map_action.input_manager.is_just_pressed('Cancel') and not self.map_action.move_roots:
            
            self.map_action.selected_battler.selected = False
            return 'explore'

        if (not self.map_action.move_roots and self.map_action.selected_battler.return_tile_location() == [cursor_tile_x * TILESIZE, cursor_tile_y * TILESIZE] and (self.map_action.input_manager.is_just_pressed('Select') or self.cursor.clicked_self)):
            if self.cursor.clicked_self:
                self.cursor.clicked_self = False

            return 'player_menu'
        
        # moves_data에서 직접 비용 계산
        move_cost = int(self.level.level_data["moves"][cursor_tile_x][cursor_tile_y])


        # 현재 캐릭터 위치에 커서가 위치할 시 루트 초기화
        if self.map_action.selected_battler.return_tile_location() == [cursor_tile_x * TILESIZE, cursor_tile_y * TILESIZE] and self.map_action.move_roots:
            while self.map_action.move_roots:
                self.map_action.move_roots[-1][0].kill()
                self.map_action.move_roots.pop()
            # self.level.visible_sprites.focus_on_target(self.map_action.selected_battler)
            self.map_action.cur_moves = self.map_action.selected_battler.stats['Mov']
            self.map_action.check_movable_from_pos(self.map_action.selected_battler.pos, self.map_action.cur_moves)
            return

        # 기존 루트의 중간 지점 클릭시 루트를 그 지점까지 Pop
        elif any(root[0].rect.topleft == cursor_pos for root in self.map_action.move_roots[:-1]):
            collided_index = next(i for i, root in enumerate(self.map_action.move_roots) if root[0].rect.topleft == cursor_pos)
            accumulated_cost = sum(root[1] for root in self.map_action.move_roots[collided_index + 1:])
            while len(self.map_action.move_roots) > collided_index + 1:
                removed_root = self.map_action.move_roots.pop()
                removed_root[0].kill()
            self.map_action.cur_moves += accumulated_cost
            self.map_action.update_path_tiles()
            last_root_pos = pygame.math.Vector2(self.map_action.move_roots[-1][0].pos) if self.map_action.move_roots else self.map_action.selected_battler.pos
            self.map_action.check_movable_from_pos(last_root_pos, self.map_action.cur_moves)
            return

        # 새로운 이동 지점 추가시
        elif ((not self.map_action.move_roots and ((abs(cursor_pos[0] - self.map_action.selected_battler.return_tile_location()[0]) == TILESIZE and cursor_pos[1] == self.map_action.selected_battler.return_tile_location()[1]) or (abs(cursor_pos[1] - self.map_action.selected_battler.return_tile_location()[1]) == TILESIZE and cursor_pos[0] == self.map_action.selected_battler.return_tile_location()[0]))) or (self.map_action.move_roots and ((abs(cursor_pos[0] - self.map_action.move_roots[-1][0].rect.x) == TILESIZE and cursor_pos[1] == self.map_action.move_roots[-1][0].rect.y) or (abs(cursor_pos[1] - self.map_action.move_roots[-1][0].rect.y) == TILESIZE and cursor_pos[0] == self.map_action.move_roots[-1][0].rect.x)))) and not self.map_action.selected_battler.inactive:

            if move_cost != -1 and move_cost <= self.map_action.cur_moves:
                self.map_action.move_roots.append([
                    Tile((cursor_pos[0], cursor_pos[1]),
                        [self.map_action.visible_sprites, self.map_action.obstacle_sprites],
                        'move_root'),
                    move_cost
                ])
                self.map_action.cur_moves -= move_cost
                self.map_action.update_path_tiles()
                self.map_action.check_movable_from_pos(pygame.math.Vector2(cursor_pos) // TILESIZE, self.map_action.cur_moves)
                return
        # 이동 실행 전에 최종 목적지 체크
        if (self.map_action.move_roots and (self.map_action.input_manager.is_just_pressed('Select') or self.cursor.clicked_self) and str(self) == 'player_control') and not self.map_action.selected_battler.inactive:
            if self.cursor.clicked_self:
                self.cursor.clicked_self = False
            final_destination = self.map_action.move_roots[-1][0].rect.topleft
            character_at_destination = any(
                battler != self.map_action.selected_battler and 
                [battler.collision_rect.x, battler.collision_rect.y] == [final_destination[0], final_destination[1]] and 
                not battler.isdead
                for battler in self.level.battler_sprites
            )
            
            if not character_at_destination:
                self.map_action.current_dialog = ConfirmationDialog()
class Player_Moving_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
    def enter(self):
        self.cursor.move_lock = True
        self.cursor.SW_select = False
        self.map_action.selected_battler.isfollowing_root = True
    def exit(self):
        self.map_action.selected_battler.isfollowing_root = False
    def update(self):
        if not self.map_action.selected_battler.isacting:
            for battler in self.level.battler_sprites:
                if (battler != self.map_action.selected_battler and battler.pos == self.map_action.selected_battler.pos and battler.team == self.map_action.selected_battler.team and not battler in self.map_action.interacted_battlers):
                    self.map_action.interacted_battlers.append(battler)
                    # 상호작용을 통한 버프 적용이 아닌 실제 이동을 통한 버프 적용
                    for skill_name, skill_level in battler.skills.items():
                        skill_info = SKILL_PROPERTIES.get(skill_name, {})
                        applied_effects = False
                        if skill_info.get('Type') != 'Passive':
                            continue
                        # 회복 효과 처리 (보좌)
                        if skill_info.get('Support_type') == 'Recovery':
                            if 'Support' in skill_info:
                                applied_effects = True
                                support_values = skill_info['Support'][skill_level]
                                for stat, value in support_values.items():
                                    if stat == 'Cur_HP':
                                        heal_amount = value
                                        self.map_action.selected_battler.Cur_HP = min(self.map_action.selected_battler.stats["Max_HP"], self.map_action.selected_battler.Cur_HP + heal_amount)
                                        self.map_action.animation_manager.create_animation((self.map_action.selected_battler.collision_rect.centerx, self.map_action.selected_battler.collision_rect.top - 10), 'DAMAGE', value=heal_amount)
                        # 소유자의 스탯 기반 버프 (전장의 함성)
                        elif skill_info.get('Support_type') == 'Boost':
                            if 'Support_%' in skill_info:
                                applied_effects = True
                                buff_data = {'percent': {}}
                                for stat, percent in skill_info['Support_%'][skill_level].items():
                                    buff_value = int(battler.stats[stat] * (percent / 100))
                                    buff_data['percent'][stat] = buff_value
                                self.map_action.apply_buff(self.map_action.selected_battler, f"temp_boost_{skill_name}", buff_data, turns=0)
                        # 대상의 기본 스탯 버프 (전장의 질주, 전장의 찬가)
                        elif skill_info.get('Support_type') == 'Boost_self':
                            applied_effects = True
                            # 고정값 버프 처리 (전장의 질주)
                            if 'Support' in skill_info:
                                buff_data = {'flat': {}}
                                for stat, value in skill_info['Support'][skill_level].items():
                                    buff_data['flat'][stat] = value
                                self.map_action.apply_buff(self.map_action.selected_battler, f"temp_boost_self_{skill_name}", buff_data, turns=0)
                            
                            # 퍼센트 기반 버프 처리 (전장의 찬가)
                            if 'Support_%' in skill_info:
                                buff_data = {'percent': {}}
                                for stat, percent in skill_info['Support_%'][skill_level].items():
                                    buff_data['percent'][stat] = percent
                                self.map_action.apply_buff(self.map_action.selected_battler, f"temp_boost_self_{skill_name}", buff_data, turns=0)
                        if applied_effects:
                            # 지원 효과 발동시 애니메이션 표시
                            self.map_action.animation_manager.create_animation(self.map_action.selected_battler, 'AURA', wait=True)
            # 이동해야할 경로가 존재함.
            if self.map_action.move_roots:
                target_battlers = [battler for battler in self.level.battler_sprites if battler != self.map_action.selected_battler and battler not in self.map_action.interacted_battlers and battler.team != self.map_action.selected_battler.team]
                if any(self.map_action.move_roots[0][0].pos == battler.pos for battler in target_battlers):      # 충돌 검사
                    for battler in target_battlers:
                        # 이동할 경로에 상호작용 안했던 배틀러가 존재
                        if self.map_action.move_roots[0][0].pos == battler.pos and not battler in self.map_action.interacted_battlers:
                            self.map_action.selected_battler.update_facing_direction(self.map_action.move_roots[0][0].pos - self.map_action.selected_battler.pos)
                            self.map_action.target_battler = battler
                            self.map_action.interacted_battlers.append(battler)
                            return 'interact','contact'
                            # 상호작용했던 배틀러에 추가해서 중복 적용 방지.
                # 단순 이동 중 1칸 이동 완료 시
                elif self.map_action.move_roots[0][0].pos == self.map_action.selected_battler.pos:
                    self.map_action.move_roots[0][0].kill()
                    self.map_action.move_roots.pop(0)
                # 단순 이동 중 1칸 이동 중일 때
                else:                
                    dx, dy = self.map_action.move_roots[0][0].rect.centerx - 0.5 * TILESIZE - self.map_action.selected_battler.return_tile_location()[0], self.map_action.move_roots[0][0].rect.centery - TILESIZE - self.map_action.selected_battler.return_tile_location()[1]
                    self.map_action.selected_battler.actlist.append('move_' + ('right' if dx > 0 else 'left' if dx != 0 else 'down' if dy > 0 else 'up'))  # 한칸 이동 act 부여
            else:
                self.map_action.selected_battler.isfollowing_root = False
                return 'interact','after_battle'
class Player_Menu_State(State):
    def enter(self):
        self.level.ui.current_main_menu = 'main'
        self.level.ui.selected_menu = 'init'
        self.cursor.move_lock = True
        self.map_action.highlight_tiles_set(None, mode='Clear')

    def update(self):
        command = self.level.ui.player_menu_control()
        if not command:
            return

        action = command[0]

        if action == '스킬타겟지정':
            selected_skill = command[1]
            skill_info = SKILL_PROPERTIES[selected_skill]
            self.map_action.target = skill_info.get('target', [])
            self.map_action.skill = selected_skill
            self.map_action.skill_shape = skill_info.get('shape', None)
            self.map_action.skill_type = skill_info.get('skill_type', None)
            self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화
            return 'select_magic_target'
            
        elif action == '아이템사용':
            selected_item = command[1]
            # 인접한 타일 모두 표시 (자신 포함)
            self.map_action.item_to_use = selected_item
            self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화

            return 'select_item_target'
            
        elif action == '사격타겟지정':
            self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화
            return 'select_range_target'
            
        elif action == '대기':
            self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화
            self.map_action.endturn()
            
        elif action == '취소':
            self.cursor.move_lock = False
            self.map_action.check_movable_from_pos(self.map_action.selected_battler.pos, self.map_action.cur_moves, show=True)
            return 'player_control'
class Phase_Change_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
        self.substate = ''
        print("INIT")
    def enter(self):
        self.cursor.move_lock = True
        self.cursor.SW_select = False
        self.cursor.selected = False
        self.substate = 'change1'
    def update(self):
        if self.substate == 'change1':
            # 페이즈 전환 처리
            next_phase = None
            if self.map_action.current_phase == 'Ally':
                if [battler for battler in self.level.battler_sprites if battler.team == 'Enemy']:
                    next_phase = 'Enemy'
                    self.level.visible_sprites.focus_on_target([battler for battler in self.level.battler_sprites if battler.team == 'Enemy'][0],cursor_obj=self.level.cursor)
                    phase_anim = self.map_action.animation_manager.create_animation(None,'PHASE_CHANGE', wait=True,value=[self.level.visible_sprites.offset,'Enemy'])
                    # Enemy BGM 재생
                    self.map_action.sound_manager.play_bgm(**SOUND_PROPERTIES['ENEMY_PHASE'])

            elif self.map_action.current_phase == 'Enemy':
                if [battler for battler in self.level.battler_sprites if battler.team == 'Ally']:
                    next_phase = 'Ally'
                    self.level.visible_sprites.focus_on_target([battler for battler in self.level.battler_sprites if battler.team == 'Ally'][0],cursor_obj=self.level.cursor)
                    phase_anim = self.map_action.animation_manager.create_animation(None,'PHASE_CHANGE', wait=True,value=[self.level.visible_sprites.offset,'Player'])
                    # Ally BGM 재생
                    self.map_action.sound_manager.play_bgm(**SOUND_PROPERTIES['ALLY_PHASE'])
            if next_phase:
                self.map_action.current_phase = next_phase
                # 새로운 페이즈의 캐릭터들 활성화 및 버프 업데이트
                for battler in self.level.battler_sprites:
                    if battler.team == self.map_action.current_phase:
                        if not battler.force_inactive:
                            battler.inactive = False
                        self.map_action.update_buffs(battler)
                        hp_regen = battler.stats.get('HP_Regen', 0) + int(battler.stats['Max_HP'] * (battler.stats.get('HP_Regen%', 0) / 100))
                        mp_regen = battler.stats.get('MP_Regen', 0) + int(battler.stats['Max_MP'] * (battler.stats.get('MP_Regen%', 0) / 100))
                        if hp_regen > 0:
                            battler.Cur_HP = min(battler.stats["Max_HP"], battler.Cur_HP + hp_regen)
                        if mp_regen > 0:
                            battler.Cur_MP = min(battler.stats["Max_MP"], battler.Cur_HP + mp_regen)
                        if hasattr(battler, 'status_duration'):
                            battler.status_duration -= 1
                            if battler.status_duration <= 0:
                                battler.state = None
                                battler.status_duration = 0
                
                self.substate = 'change2'
                return
                
        elif self.substate == 'change2' and not self.map_action.animation_manager.has_active_animations():
            return 'explore'
class Interact_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
        self.substate = ''
    def enter(self,state= None):
        if state:
            self.substate = state
        
    def exit(self):
        pass
    def update(self):
# - 기본 interact. 아군일 경우 힐(스킬보유시), 적군일 경우 공격
        if self.substate == 'contact':
            if self.map_action.selected_battler.team == self.map_action.target_battler.team:
                return 'player_moving'
# - 적을 만난 경우 공격 선딜레이
            elif (self.map_action.selected_battler.team == 'Ally' and self.map_action.target_battler.team == 'Enemy') or (self.map_action.selected_battler.team == 'Enemy' and self.map_action.target_battler.team == 'Ally'):
                char_data = CharacterDatabase.data.get(self.map_action.selected_battler.char_type, {})
                if char_data.get('Class') == 'Melee':  # 근접 공격 타입일 때만 공격
                    self.map_action.current_Class = 'Melee'
                    self.map_action.selected_battler.isfollowing_root = False
                    self.map_action.selected_battler.actlist.append('act_for_attack')
                    self.map_action.update_time = pygame.time.get_ticks() + self.map_action.selected_battler.attack_delay
                    return 'interact','melee1'
                else:
                    # Range 타입은 그냥 지나감
                    return 'player_moving'
# - 데미지 계산 (_attack1) 및 ZOC 확인(발동 시 주변 타일로 이동)
        elif self.substate[:5] == 'melee':
            if self.substate == 'melee1' and (self.map_action.update_time < pygame.time.get_ticks()):
            # 공격 방향에 따른 데미지 계산
                Damage_before_direction = (self.map_action.selected_battler.stats['STR'] * 2 - self.map_action.target_battler.stats['RES']) * self.map_action.selected_battler.stats["Melee_attack_multiplier"] * self.map_action.target_battler.stats["Melee_defense_multiplier"]
                if Damage_before_direction < 0:
                    Damage_before_direction = 0
                Damage = Damage_before_direction 
                opposite_directions = {"left": "right", "right": "left", "up": "down", "down": "up"}
                if self.map_action.target_battler.facing == self.map_action.selected_battler.facing:
                    Damage = Damage_before_direction * 1.25 * self.map_action.target_battler.stats["Rear_attack_multiplier"]  # 후면 공격은 1.25배
                    ZOC_vurnerable = 15
                    evasion_vurnerable = 15
                    counter_vurnerable = 15
                    critical_vurnerable = 10
                elif self.map_action.target_battler.facing != opposite_directions.get(self.map_action.selected_battler.facing):
                    Damage = Damage_before_direction * 1.1 * self.map_action.target_battler.stats["Side_attack_multiplier"] # 측면 공격은 1.1배
                    ZOC_vurnerable = 5
                    evasion_vurnerable = 5
                    counter_vurnerable = 5
                    critical_vurnerable = 4
                else:
                    Damage = Damage_before_direction  * self.map_action.target_battler.stats["Frontal_attack_multiplier"] # 정면 공격은 정상 데미지
                    ZOC_vurnerable = 0
                    evasion_vurnerable = 0
                    counter_vurnerable = 0
                    critical_vurnerable = 0
            # 카운터 확인                    
                Counter_chance_DEX_Difference = (self.map_action.target_battler.stats["DEX"] - self.map_action.selected_battler.stats["DEX"]) * 0.5
                Counter_chance_STATS = self.map_action.target_battler.stats["Counter_Chance"]
                total_counter_chance = (Counter_chance_DEX_Difference + Counter_chance_STATS - counter_vurnerable) * 0.01
                # print(f"반격 확률 : {Counter_chance_DEX_Difference} + {Counter_chance_STATS} - {counter_vurnerable} = {total_counter_chance}")
                if total_counter_chance > random.random():
                    self.map_action.animation_manager.create_animation(self.map_action.selected_battler.collision_rect.center, 'EMOTE_SURPRISE', wait=True)
                    self.map_action.target_battler.battle_return(self.map_action.selected_battler,move_type='counter')
                    self.map_action.update_time = pygame.time.get_ticks() + 500
                    return 'interact','melee_counter1'
            # 적중률 확인
                Hit_accuracy_DEX_Difference = (self.map_action.selected_battler.stats["DEX"] - self.map_action.target_battler.stats["DEX"]) * 2
                Hit_accuracy_STATS = self.map_action.selected_battler.stats["Accuracy_rate"]- self.map_action.target_battler.stats["Melee_evasion_chance"]
                total_accuracy =  1 + (Hit_accuracy_DEX_Difference + Hit_accuracy_STATS + evasion_vurnerable) * 0.01
                # print(f"적중률 : {total_accuracy * 100}%")
                if total_accuracy < random.random():
                    self.map_action.target_battler.battle_return(self.map_action.selected_battler,move_type='evasion')
                    self.map_action.sound_manager.play_sound(**SOUND_PROPERTIES['EVASION'])                
                    return 'interact','melee2'
            # 크리티컬 확인
                Critical_Chance = self.map_action.selected_battler.stats["Critical_Chance"] + critical_vurnerable + self.map_action.selected_battler.stats["DEX"] * 0.5
                print(f"크리티컬율 : {Critical_Chance}%")
                Criticaled = False
                if random.random() < Critical_Chance * 0.01:
                    Criticaled = True
                    Damage *= self.map_action.selected_battler.stats["Critical_attack_multiplier"]
                    self.map_action.animation_manager.create_animation((self.map_action.target_battler.collision_rect.centerx, self.map_action.target_battler.collision_rect.centery), 'CRITICAL', wait=True)
                self.map_action.animation_manager.clear_active_animations()
                self.map_action.animation_manager.create_animation((self.map_action.target_battler.collision_rect.centerx, self.map_action.target_battler.collision_rect.centery), 'SLASH', wait=True)
                self.map_action.target_battler.battle_return(self.map_action.selected_battler,move_type='knockback')
                
                self.map_action.Damage(self.map_action.selected_battler,self.map_action.target_battler,Damage,"Melee")

            # Z.O.C 발동 여부 확인
                if self.map_action.target_battler.Cur_HP > 0 and not Criticaled:
                    zoc_hold_percentage = (self.map_action.target_battler.stats["ZOC_Chance"] - ZOC_vurnerable - self.map_action.selected_battler.stats["ZOC_Ignore_Chance"]) * 0.01
                    # print(f"킬 실패 시 Z.O.C 확률 적용 : {zoc_hold_percentage * 100}%")
                    if 0 < zoc_hold_percentage and random.random() < (zoc_hold_percentage):
                        self.map_action.animation_manager.create_animation((self.map_action.target_battler.collision_rect.midtop[0], self.map_action.target_battler.collision_rect.midtop[1]), 'SHIELD', wait=True)



                        # Z.O.C가 발동되었을 때 이동 경로 취소
                        while self.map_action.move_roots:
                            self.map_action.move_roots[-1][0].kill()
                            self.map_action.move_roots.pop()
                        if self.map_action.selected_battler.actlist[0] == 'act_for_attack':
                            self.map_action.selected_battler.wait_time -= 5000
                        return 'interact','melee_ZOC1'
                        return
            # ZOC 미발동 시 후딜레이 정상 적용
                self.map_action.update_time = pygame.time.get_ticks() + self.map_action.selected_battler.attack_delay
                return 'interact','melee2'
    # - ZOC 발동 후 이동까지 대기 + 방어 애니메이션 완료까지 대기 (_attack_ZOC1)
            elif self.substate == 'melee_ZOC1' and not self.map_action.animation_manager.has_active_animations():
                # 주변에 빈 타일 찾기
                gotopos = None
                # 제자리 이동가능한가?
                i = 1
                if any(self.map_action.selected_battler.pos == battler.pos for battler in self.level.battler_sprites if battler != self.map_action.selected_battler):
                    while(not gotopos):
                        movable_tiles = self.map_action.check_movable_from_pos(self.map_action.selected_battler.pos, i, show=False)
                        for movable_tile in movable_tiles:
                            if all(movable_tile[0] != battler.pos for battler in self.level.battler_sprites if battler != self.map_action.selected_battler):
                                gotopos = movable_tile[0]
                                break
                        i += 1
                # 가장 가까운 이동가능한 타일을 검색함
                if gotopos is not None:
                    self.map_action.selected_battler.Goto.x += (gotopos[0] * TILESIZE - self.map_action.selected_battler.return_tile_location()[0])
                    self.map_action.selected_battler.Goto.y += (gotopos[1] * TILESIZE - self.map_action.selected_battler.return_tile_location()[1])
                    self.map_action.selected_battler.ismove = True
                    self.map_action.selected_battler.pos = pygame.math.Vector2(gotopos[0], gotopos[1])
                return 'interact','melee_ZOC2'

            elif self.substate == 'melee_ZOC2' and not self.map_action.selected_battler.ismove:
                self.map_action.animation_manager.create_animation(self.map_action.selected_battler.collision_rect.center, 'EMOTE_DESPAIR', wait=True)
                # Z.O.C 스킬 레벨 확인 및 상태이상 적용
                zoc_level = self.map_action.target_battler.skills.get('Z.O.C', 1)
                status_chances = SKILL_PROPERTIES['Z.O.C']['Status_%'].get(zoc_level, {})
                
                # 상태이상 확률 체크 및 적용
                for status, chance in status_chances.items():
                    if random.random() * 100 < chance:  # % 확률 체크
                        self.map_action.apply_status(self.map_action.selected_battler,status, 3)  # 3턴 지속
                return 'interact','melee_ZOC3'
                
            elif self.substate == 'melee_ZOC3' and not self.map_action.animation_manager.has_active_animations():
                return 'interact','after_battle'
    # - 공격 후 딜레이 후 이동 (_attack2)
            elif self.substate == 'melee2' and self.map_action.update_time < pygame.time.get_ticks():
                self.map_action.selected_battler.isfollowing_root = True
                return 'player_moving'

            elif self.substate == 'melee_counter1' and self.map_action.update_time < pygame.time.get_ticks():
                Damage = (self.map_action.target_battler.stats['DEX'] + self.map_action.target_battler.stats['STR'] - self.map_action.selected_battler.stats["RES"]) * self.map_action.target_battler.stats["Melee_attack_multiplier"] * self.map_action.selected_battler.stats["Melee_defense_multiplier"] * self.map_action.selected_battler.stats["Counter_attack_multiplier"]
                self.map_action.animation_manager.create_animation((self.map_action.selected_battler.collision_rect.centerx, self.map_action.selected_battler.collision_rect.centery), 'SLASH', wait=True)
                self.map_action.animation_manager.create_animation((self.map_action.selected_battler.collision_rect.centerx, self.map_action.selected_battler.collision_rect.top - 10),'DAMAGE', value=-Damage)
                self.map_action.Damage(self.map_action.target_battler,self.map_action.selected_battler,Damage,"Melee")
                while self.map_action.move_roots:
                    self.map_action.move_roots[-1][0].kill()
                    self.map_action.move_roots.pop()
                gotopos = None
                i = 1
                if any(self.map_action.selected_battler.pos == battler.pos for battler in self.level.battler_sprites if battler != self.map_action.selected_battler):
                    while(not gotopos):
                        movable_tiles = self.map_action.check_movable_from_pos(self.map_action.selected_battler.pos, i, show=False)
                        for movable_tile in movable_tiles:
                            if all(movable_tile[0] != battler.pos for battler in self.level.battler_sprites if battler != self.map_action.selected_battler):
                                gotopos = movable_tile[0]
                                break
                        i += 1
                if gotopos is not None:
                    self.map_action.selected_battler.Goto.x += (gotopos[0] * TILESIZE - self.map_action.selected_battler.return_tile_location()[0])
                    self.map_action.selected_battler.Goto.y += (gotopos[1] * TILESIZE - self.map_action.selected_battler.return_tile_location()[1])
                    self.map_action.selected_battler.ismove = True
                    self.map_action.selected_battler.pos = pygame.math.Vector2(gotopos[0], gotopos[1])
                return 'interact','melee_counter2'

            elif self.substate == 'melee_counter2' and not self.map_action.selected_battler.ismove:
                self.map_action.update_time = pygame.time.get_ticks() + 1000
                return 'interact','melee_counter3'

            elif self.substate == 'melee_counter3' and self.map_action.update_time < pygame.time.get_ticks():
            
                return 'interact','after_battle'
#   원거리 공격 처리
        elif self.substate[:5] == 'range':
            self.level.cursor.move_lock = True
            if self.substate == 'range0':
                self.level.cursor.move_lock = True
                self.map_action.highlight_tiles_set(None,mode='Clear')
                self.map_action.visible_sprites.focus_on_target(self.map_action.selected_battler)
                self.map_action.visible_sprites.toggle_zoom()
                self.map_action.visible_sprites.zoom_to_battler(self.map_action.selected_battler)

                self.map_action.selected_battler.update_facing_direction(self.map_action.target_battler.pos - self.map_action.selected_battler.pos)
                self.map_action.selected_battler.actlist.append('range_attack')
                self.map_action.sound_manager.play_sound(**SOUND_PROPERTIES['ARROW_FLYING'])   
                self.map_action.sound_manager.play_sound(**SOUND_PROPERTIES['SHOOT_ARROW'])   

                self.map_action.update_time = pygame.time.get_ticks() + self.map_action.selected_battler.attack_delay + 500
                return 'interact','range1'
            if self.substate == 'range1' and pygame.time.get_ticks() > self.map_action.update_time:
             

                self.level.visible_sprites.focus_on_target(self.map_action.target_battler)
                self.map_action.update_time = pygame.time.get_ticks() + 500
                return 'interact','range2'
            elif self.substate == 'range2' and pygame.time.get_ticks() > self.map_action.update_time:
                range_accuracy_Stats = self.map_action.selected_battler.stats["Accuracy_rate"] - self.map_action.target_battler.stats["Ranged_evasion_chance"]
                range_accuracy_DEX_Difference = (self.map_action.selected_battler.stats["DEX"] - self.map_action.target_battler.stats["DEX"]) * 0.02
                range_accuracy = range_accuracy_Stats + range_accuracy_DEX_Difference
                # print(f"원거리 적중률 : {range_accuracy * 100}%")
                if range_accuracy > random.random():
                    Damage = (self.map_action.selected_battler.stats['STR'] + self.map_action.selected_battler.stats['DEX'] - self.map_action.target_battler.stats['RES']) *  self.map_action.target_battler.stats["Ranged_defense_multiplier"] * self.map_action.selected_battler.stats["Ranged_attack_multiplier"]
                    Critical_Chance = self.map_action.selected_battler.stats["Critical_Chance"] + self.map_action.selected_battler.stats["DEX"] * 0.6
                    print(f"크리티컬율 : {Critical_Chance}%")
                    if random.random() < Critical_Chance * 0.01:
                        Criticaled = True
                        Damage *= self.map_action.selected_battler.stats["Critical_attack_multiplier"]
                        self.map_action.animation_manager.create_animation((self.map_action.target_battler.collision_rect.centerx, self.map_action.target_battler.collision_rect.centery), 'CRITICAL', wait=True)
                        
                    self.map_action.animation_manager.clear_active_animations()
                    self.map_action.animation_manager.create_animation(self.map_action.target_battler.collision_rect.center, 'RANGE_HIT', wait=True)
                    self.map_action.target_battler.battle_return(self.map_action.selected_battler,move_type='knockback')

                    # 공격 데미지 계산
                    if Damage < 0:
                        Damage = 0
                    
                    self.map_action.Damage(self.map_action.selected_battler,self.map_action.target_battler,Damage,"Range")
        

                    self.map_action.update_time = pygame.time.get_ticks() + 500
                    return 'interact','range3'
                else:
                    self.map_action.target_battler.battle_return(self.map_action.selected_battler,move_type='range_evasion')
                    self.map_action.update_time = pygame.time.get_ticks() + 500
                    return 'interact','range3'
            elif self.substate == 'range3' and self.map_action.update_time < pygame.time.get_ticks():
                return 'interact','after_battle'
#   스킬 애니메이션 생성 처리(_skill), 배틀러가 행동(casting)을 마무리할 때 처리 시작
        elif self.substate[:5] == 'skill':
            if self.substate == 'skill':
                self.map_action.selected_battler.Cur_MP -= SKILL_PROPERTIES[self.map_action.skill].get('Mana', {}).get(self.map_action.selected_battler.skills[self.map_action.skill], 0)
                if self.map_action.selected_battler.Cur_MP < 0:
                    raise ValueError("마나가 부족함에도 스킬사용 시도됨.")
                self.level.visible_sprites.focus_on_target(self.map_action.selected_battler)
                self.level.cursor.rect.center = self.map_action.selected_battler.collision_rect.center
                self.level.cursor.move_lock = True
                self.level.cursor.SW_select = True
                self.map_action.selected_battler.update_facing_direction(self.level.cursor.pos - self.map_action.selected_battler.pos)
                self.map_action.selected_battler.actlist.append('casting')
                self.map_action.visible_sprites.toggle_zoom()
                self.map_action.visible_sprites.zoom_to_battler(self.map_action.selected_battler)
                if SKILL_PROPERTIES[self.map_action.skill].get('casting', []) != 'default':
                    self.map_action.animation_manager.create_animation((self.map_action.selected_battler.return_tile_location()[0],self.map_action.selected_battler.return_tile_location()[1] - TILESIZE),SKILL_PROPERTIES[self.map_action.skill].get('casting', []), wait=True)
                self.substate = 'skill1'
            elif self.substate == 'skill1' and not self.map_action.selected_battler.isacting:
                self.map_action.visible_sprites.toggle_zoom()
                if isinstance(self.map_action.target_battler, list):
                    targets = self.map_action.target_battler    
                else:
                    targets = [self.map_action.target_battler]
                    self.level.visible_sprites.focus_on_target(self.map_action.target_battler)
                
                animate_type = SKILL_PROPERTIES[self.map_action.skill].get('animate_type', 'target')
                if animate_type == 'sequentially':
                    # 타일 위치들을 플레이어로부터의 거리 순으로 정렬
                    tile_positions = [tile for tile in self.map_action.highlight_tiles]
                    tile_positions.sort(key=lambda tile: abs(tile.pos.x - self.map_action.selected_battler.pos.x) + 
                                                    abs(tile.pos.y - self.map_action.selected_battler.pos.y))
                    # 첫 번째 타일에 대한 애니메이션 생성
                    if tile_positions:
                        self.map_action.animation_manager.create_animation((tile_positions[0].pos.x, tile_positions[0].pos.y),SKILL_PROPERTIES[self.map_action.skill].get('animate', 'SLASH'),wait=True)
                        # 타겟 중에서 첫 번째 타일에 있는 대상에게 데미지
                        for target in targets:
                            if target.pos == tile_positions[0].pos:
                                self.map_action.apply_skill_effects(target)
                    
                    self.sequence_tiles = tile_positions[1:]  # 남은 타일들 저장
                    self.sequence_delay = SKILL_PROPERTIES[self.map_action.skill].get('sequence_delay', 0.3)
                    self.next_sequence_time = pygame.time.get_ticks() + self.sequence_delay * 1000
                    return 'interact','skill_sequence'
                
                elif animate_type == 'all_tiles':
                    # 타일 위치들 저장
                    tile_positions = [(tile.rect.centerx, tile.rect.centery) for tile in self.map_action.highlight_tiles]
                    # 타일 제거 전에 모든 위치에 애니메이션 생성
                    for pos_x, pos_y in tile_positions:
                        self.map_action.animation_manager.create_animation((pos_x, pos_y),SKILL_PROPERTIES[self.map_action.skill].get('animate', 'SLASH'),wait=True)

                elif animate_type == 'battler':
                    size_multiplier = SKILL_PROPERTIES[self.map_action.skill].get('animation_size', 2.0)
                    self.map_action.animation_manager.create_animation((self.map_action.selected_battler.collision_rect.centerx, self.map_action.selected_battler.collision_rect.centery),SKILL_PROPERTIES[self.map_action.skill].get('animate', 'SLASH'),wait=True,size=size_multiplier)
                    
                else:  # 'target'
                    for target in targets:
                        self.map_action.animation_manager.create_animation((target.collision_rect.midtop[0], target.collision_rect.midtop[1]),SKILL_PROPERTIES[self.map_action.skill].get('animate', 'SLASH'),wait=True)
                    
                        
                self.TEMP_wait_time = pygame.time.get_ticks() + SKILL_PROPERTIES[self.map_action.skill].get('Dmg_timing', 0)
                return 'interact','skill2'
    #   스킬 데미지를 입힐 타이밍 계산(_skill2)
            elif self.substate == 'skill2' and pygame.time.get_ticks() > self.TEMP_wait_time:
                del self.TEMP_wait_time
                targets = self.map_action.target_battler if isinstance(self.map_action.target_battler, list) else [self.map_action.target_battler]
                
                for target in targets:
                    skill_info = SKILL_PROPERTIES[self.map_action.skill]
                    skill_level = self.map_action.selected_battler.skills[self.map_action.skill]
                    
                    # 군의학 스킬 처리
                    if self.map_action.skill == '군의학':
                        heal_amount = skill_info['Value'][skill_level]['Cur_HP']
                        
                        # 최대 HP를 초과하지 않도록 회복
                        if target.Cur_HP + heal_amount > target.stats["Max_HP"]:
                            target.Cur_HP = target.stats["Max_HP"]
                        else:
                            target.Cur_HP += heal_amount
                            
                        # 힐링 애니메이션
                        self.map_action.animation_manager.create_animation((target.collision_rect.centerx, target.collision_rect.top - 10),'DAMAGE',value=heal_amount)
                        self.map_action.animation_manager.create_animation((target.collision_rect.centerx, target.collision_rect.centery),skill_info.get('animate', 'HEAL'))                            
                    # 버프 스킬 처리
                    elif skill_info['skill_type'] == 'buff':
                        # 두 가지 버프 타입 모두 확인
                        percent_buffs = skill_info.get('Buff_%', {}).get(skill_level, {})
                        flat_buffs = skill_info.get('Buff', {}).get(skill_level, {})
                        
                        # 버프 데이터 구성
                        buff_data = {'percent': percent_buffs,'flat': flat_buffs}
                        self.map_action.apply_buff(target,self.map_action.skill,buff_data,skill_info.get('duration', 2))
                        
                        # 버프 적용 애니메이션
                        self.map_action.animation_manager.create_animation((target.collision_rect.centerx, target.collision_rect.centery),SKILL_PROPERTIES[self.map_action.skill].get('animate', 'SHIELD'),wait=True)
                        
                    # 데미지 스킬 처리
                    else:
                        # 데미지 계산
                        target_magic_def = target.stats["INT"] * 1.2 + target.stats["RES"] * 0.4
                        level_diff_bonus = (self.map_action.selected_battler.stats["INT"] - target.stats["INT"]) * 0.015 * target.stats["Magic_defense_multiplier"] * self.map_action.selected_battler.stats["Magic_attack_multiplier"] # 기본 보너스 계산
                        # 각 타겟의 stats 적용

                        skill_multiplier = skill_info.get('Dmg_Coff', {}).get(skill_level, 0)
                        Damage = ((1 + level_diff_bonus) * skill_multiplier * 1.5) - target_magic_def
                        if Damage < 0:
                            Damage = 0
                            
                        # 데미지 적용
                        self.map_action.Damage(self.map_action.selected_battler,target,Damage,"Magic")
       
                        if target.Cur_HP > 0:
                            # 상태이상 적용 확률 체크
                            if 'Status_%' in skill_info:
                                status_chances = skill_info['Status_%'].get(skill_level, {})
                                for status, chance in status_chances.items():
                                    if random.random() * 100 < chance:  # % 확률 체크
                                        self.map_action.apply_status(target,status, 2)  # 2턴 지속
                        # 데미지 애니메이션
                        self.map_action.animation_manager.create_animation((target.collision_rect.centerx, target.collision_rect.top - 10),'DAMAGE',value=-Damage)
                return 'interact','skill3'
    #   스킬이 다 사라지면(_skill3) after_battle로 전환
            elif self.substate == 'skill_sequence':
                if pygame.time.get_ticks() >= self.next_sequence_time and self.sequence_tiles:
                    # 다음 타일 애니메이션 생성
                    tile = self.sequence_tiles.pop(0)
                    self.map_action.animation_manager.create_animation(tile,SKILL_PROPERTIES[self.map_action.skill].get('animate', 'SLASH'),wait=True)
                    # 해당 타일에 있는 타겟에게 데미지
                    targets = self.map_action.target_battler if isinstance(self.map_action.target_battler, list) else [self.map_action.target_battler]
                    for target in targets:
                        if target.pos == tile.pos:
                            self.map_action.apply_skill_effects(target)
                    
                    if self.sequence_tiles:  # 아직 남은 타일이 있으면
                        self.next_sequence_time = pygame.time.get_ticks() + self.sequence_delay * 1000
                    else:  # 모든 타일 처리 완료
                        return 'interact','skill3'

            elif self.substate == 'skill3' and not self.map_action.animation_manager.has_active_animations():
                self.map_action.highlight_tiles_set(None,mode='Clear')
                return 'interact','after_battle'
#   배틀 종료 후 사망 여부 판정 (_interact_after_battle)
        elif self.substate[:12] == 'after_battle':
            if self.substate == 'after_battle':
                self.map_action.process_exp_gain()
                self.map_action.visible_sprites.toggle_zoom()
                if any(battler.Cur_HP == 0 for battler in self.level.battler_sprites):
                    self.map_action.update_time = pygame.time.get_ticks() + 500
                    return 'interact','after_battle_death1'
    #   아무것도 사망하지 않으면 캐릭터 턴 종료
                else:
                    print('endturn')
                    self.map_action.endturn()

            elif self.substate == 'after_battle_death1' and self.map_action.update_time < pygame.time.get_ticks():
                for battler in self.level.battler_sprites:
                    if battler.Cur_HP == 0:

                        # 경험치 획득 및 레벨업 처리
                        battler.death()  # 예시: 배틀러를 죽이는 메서드 호출
                return 'interact','after_battle_death2'           
#   사망한 배틀러가 존재할 시 해당 배틀러들이 isdead를 띄울 때까지 대기, 이 후 객체 kill (_interact_death)
            elif self.substate == 'after_battle_death2' and all((battler.Cur_HP <= 0 and battler.isdead) or battler.Cur_HP > 0 for battler in self.level.battler_sprites):
                for battler in self.level.battler_sprites:
                    if battler.Cur_HP <= 0:
                        battler.kill()
                self.map_action.update_time = pygame.time.get_ticks() + 1000
                return 'interact','after_battle_death3'

            elif self.substate == 'after_battle_death3' and self.map_action.update_time < pygame.time.get_ticks():
                self.map_action.endturn()

        elif self.substate[:10] == 'using_item':
            if self.substate == 'using_item1':
                item_data = ITEM_PROPERTIES[self.map_action.item_to_use]
                if 'animate' in item_data:
                    self.map_action.animation_manager.create_animation(self.map_action.target_battler,item_data['animate'],wait=True)
                return 'interact','using_item2' 
            elif self.substate == 'using_item2' and not self.map_action.animation_manager.has_active_animations():
                self.map_action.update_time = pygame.time.get_ticks() + 300
                return 'interact','using_item3'
            elif self.substate == 'using_item3' and self.map_action.update_time < pygame.time.get_ticks():
                self.map_action.use_item(self.map_action.target_battler, self.map_action.item_to_use)
                self.map_action.update_time = pygame.time.get_ticks() + 800
                return 'interact','using_item4'
            elif self.substate == 'using_item4' and self.map_action.update_time < pygame.time.get_ticks():
                self.level.ui.current_item_menu_index = 0
                self.map_action.endturn()
class Select_Magic_Target_State(State):
    def enter(self):

        self.map_action.temp_facing = self.map_action.selected_battler.facing  # 임시 방향 초기화
        attackable_pos = self.map_action.check_magic_range(self.map_action.selected_battler,self.map_action.skill)
        self.level.cursor.move_lock = False
        self.level.cursor.SW_select = False
        self.level.cursor.select_lock = True
        self.map_action.highlight_tiles_set([pygame.math.Vector2(x,y)for x , y in attackable_pos], mode = 'Set')
    def update(self):
        # 대화상자 처리
        if ['Self'] == SKILL_PROPERTIES[self.map_action.skill]['target']:
            self.map_action.target_battler = self.map_action.selected_battler
            return 'interact','skill'
        if self.map_action.current_dialog:
            self.map_action.current_dialog.draw()
            self.level.cursor.move_lock = True  # 커서 이동 확실히 잠금
            result = self.map_action.current_dialog.handle_input(self.map_action.input_manager)
            if result is not None:
                if result:  # 사용 확인
                    if self.map_action.target_battler:
                        self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화
                        self.map_action.highlight_tiles_set(None,mode='Invisible')
                        self.map_action.current_dialog = None
                        return 'interact','skill'
                else:
                    self.level.cursor.move_lock = False  # 커서 이동 잠금 해제
                    self.map_action.target_battler = None
                self.map_action.current_dialog = None
            return
        
        # 직선형 스킬일 때 방향 변경 처리
        if SKILL_PROPERTIES[self.map_action.skill].get('shape') == 'linear':
            new_facing = None
            cursor_x = self.level.cursor.pos.x
            cursor_y = self.level.cursor.pos.y
            battler_x = self.map_action.selected_battler.pos.x
            battler_y = self.map_action.selected_battler.pos.y

            # x좌표가 같은 라인
            if cursor_x == battler_x:
                new_facing = 'down' if cursor_y > battler_y else 'up'
            elif cursor_y == battler_y:
                new_facing = 'right' if cursor_x > battler_x else 'left'
            # 방향이 바뀌었다면 타일 재생성
            if new_facing and new_facing != self.map_action.temp_facing:
                self.map_action.temp_facing = new_facing
                
                self.map_action.highlight_tiles_set(None,mode='Clear')
                self.map_action.check_magic_range(self.map_action.selected_battler,self.map_action.skill)
                attackable_pos = self.map_action.check_magic_range(self.map_action.selected_battler,self.map_action.skill)
                self.map_action.highlight_tiles_set([pygame.math.Vector2(x,y)for x , y in attackable_pos], mode = 'Set')

        if self.map_action.input_manager.is_just_pressed('Cancel'):
            self.map_action.selected_battler.facing = self.map_action.selected_battler.facing  # 원래 방향 복원
            self.level.ui.current_main_menu = 'skill'
            self.map_action.highlight_tiles_set(None,mode='Clear')
            self.level.visible_sprites.focus_on_target(self.map_action.selected_battler,cursor_obj=self.level.cursor)
            self.level.cursor.move_lock = True
            self.level.cursor.SW_select = True
            self.level.cursor.select_lock = False
            self.map_action.skill = None
            return 'player_menu'

        if (self.map_action.input_manager.is_just_pressed('Select') or self.level.cursor.clicked_self):
            if self.level.cursor.clicked_self:
                self.level.cursor.clicked_self = False
            skill_type = SKILL_PROPERTIES[self.map_action.skill].get('skill_type', {})
            skill_targets = SKILL_PROPERTIES[self.map_action.skill]['target']
            self.map_action.current_Class = 'Magic'
            # 강조된 타일 위에 커서가 올려졌을 때 조건문 실행
            if any(self.level.cursor.pos == pygame.math.Vector2(attackable_tile.rect.topleft[0] // TILESIZE, attackable_tile.rect.topleft[1] // TILESIZE) for attackable_tile in self.map_action.highlight_tiles):
                # 단일 타게팅 
                if skill_type == 'Targeting':
                    self.map_action.target_battler = None
                    for battler in self.level.battler_sprites:
                        if self.level.cursor.pos == battler.pos:
            # 타게팅 분류
                            if (('Self_Ally' in skill_targets and (battler.team == self.map_action.selected_battler.team)) or
                                ('Self_Ally_except_Self' in skill_targets and (battler.team == self.map_action.selected_battler.team) and battler != self.map_action.selected_battler) or
                                ('Self_Enemy' in skill_targets and not (battler.team == self.map_action.selected_battler.team))):
                                self.map_action.target_battler = battler
                                break
                # 범위 타게팅 수정
                elif skill_type == 'Targeting_all':
                    self.map_action.target_battler = []

                    skill_area = [tile.pos for tile in self.map_action.highlight_tiles]
                    
                    for battler in self.level.battler_sprites:
                        if battler.pos in skill_area:
                            team_match = (battler.team == self.map_action.selected_battler.team)
                            if (('Self_Ally' in skill_targets and team_match) or
                                ('Self_Ally_except_Self' in skill_targets and team_match and battler != self.map_action.selected_battler) or
                                ('Self_Enemy' in skill_targets and not team_match)):
                                self.map_action.target_battler.append(battler)

                # 타겟이 있으면 확인 대화상자 표시
                if self.map_action.target_battler:
                    self.level.cursor.move_lock = True
                    self.level.cursor.select_lock = True
                    self.map_action.current_dialog = ConfirmationDialog("사용하시겠습니까?")
class Select_Range_Target_State(State):
    def enter(self):
        self.cursor.move_lock = False
        attack_range = CharacterDatabase.data.get(self.map_action.selected_battler.char_type, {}).get('Range')
        self.map_action.current_Class = 'Range'
        # 다이아몬드 형태의 범위 계산
        diamond = [(dx, dy) for dx in range(-attack_range, attack_range + 1) 
                for dy in range(-attack_range, attack_range + 1) 
                if abs(dx) + abs(dy) <= attack_range]
        
        # 공격 가능한 타일 위치 확인
        check_diamond = []
        for tiledxdy in diamond:
            check_tile = self.map_action.get_tiles_in_line(self.map_action.selected_battler.pos,self.map_action.selected_battler.pos + pygame.math.Vector2(tiledxdy))
            if all(not tile['blocked'] for tile in check_tile):
                check_diamond.append(self.map_action.selected_battler.pos + pygame.math.Vector2(tiledxdy))
        self.map_action.highlight_tiles_set(check_diamond, mode = 'Set')
        
    def exit(self):
        self.map_action.highlight_tiles_set(None,mode='Clear')
    def update(self):
        # 처음 모드에 진입할 때만 범위 표시
        if self.map_action.current_dialog:
            self.map_action.current_dialog.draw()
            self.level.cursor.move_lock = True
            result = self.map_action.current_dialog.handle_input(self.map_action.input_manager)
            if result is not None:
                self.map_action.current_dialog = None
                self.level.cursor.move_lock = False
                if result:
                    return 'interact','range0'
            return

            # 캐릭터의 공격 범위 가져오기

        
        # 커서 위치까지의 경로 타일 계산
        line_tiles = self.map_action.get_tiles_in_line(self.map_action.selected_battler.pos,self.level.cursor.pos)
        
        # 취소 처리
        if self.map_action.input_manager.is_just_pressed('Cancel'):
            # 모든 타일 제거
            self.level.ui.current_main_menu = 'main'
            self.level.ui.selected_menu = 'init'
            self.level.cursor.move_lock = True
            self.level.cursor.SW_select = True
            self.level.cursor.rect.center = self.map_action.selected_battler.collision_rect.center
            self.level.cursor.pos = self.map_action.selected_battler.pos
            return 'player_menu'
        # 선택 처리
        elif (self.map_action.input_manager.is_just_pressed('Select') or self.level.cursor.clicked_self):
            if self.level.cursor.clicked_self:
                self.level.cursor.clicked_self = False
            # 적이 커서 위치에 있는지 확인
            for battler in self.level.battler_sprites:
                if (battler.pos == self.level.cursor.pos and battler.team != self.map_action.selected_battler.team and any(battler.pos == tile.pos for tile in self.map_action.highlight_tiles)):
                    self.map_action.target_battler = battler
                    self.level.cursor.move_lock = True
                    self.map_action.current_dialog = ConfirmationDialog("공격하시겠습니까?")
class Select_Item_Target_State(State):
    def enter(self):
        adjacent_tiles = [(0,0), (0,1), (0,-1), (1,0), (-1,0)]
        highlight_tiles = []
        # 먼저 타일 생성
        for dx, dy in adjacent_tiles:
            check_pos = self.map_action.selected_battler.pos + pygame.math.Vector2(dx, dy)
            # 맵 범위 체크
            if (0 <= check_pos.x < len(self.level.level_data["moves"][0]) and 0 <= check_pos.y < len(self.level.level_data["moves"])):
                highlight_tiles.append(check_pos)
        self.map_action.highlight_tiles_set(highlight_tiles, mode='Set')
        self.cursor.move_lock = False
    def update(self):
        """아이템 사용 대상 선택"""
        if self.map_action.current_dialog:
            self.map_action.current_dialog.draw()
            self.map_action.level.cursor.move_lock = True
            result = self.map_action.current_dialog.handle_input(self.map_action.input_manager)
            if result is not None:
                if result:
                    self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화
                    self.map_action.level.cursor.move_lock = True
                    # 타일 제거
                    self.map_action.highlight_tiles_set(None,mode='Clear')
                    
                    # 아이템 사용
                    item_data = ITEM_PROPERTIES[self.map_action.item_to_use]
                    if 'animate' in item_data:
                        self.map_action.animation_manager.create_animation(self.map_action.target_battler,item_data['animate'],wait=True)
                    self.map_action.current_dialog = None
                    return 'interact','using_item1'
                else:
                    self.map_action.level.cursor.move_lock = False
                self.map_action.current_dialog = None
                return
        if self.map_action.input_manager.is_just_pressed('Cancel'):
            # 타일 제거
            self.map_action.highlight_tiles_set(None,mode='Clear')
            self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화
            self.map_action.level.ui.current_main_menu = 'item'
            self.map_action.level.cursor.move_lock = True
            self.map_action.level.cursor.SW_select = True
            self.map_action.level.cursor.rect.center = self.map_action.selected_battler.collision_rect.center
            self.map_action.level.cursor.pos = self.map_action.selected_battler.pos
            return 'player_menu'
            
        elif (self.map_action.input_manager.is_just_pressed('Select') or self.map_action.level.cursor.clicked_self):
            if self.map_action.level.cursor.clicked_self:
                self.map_action.level.cursor.clicked_self = False
            # 커서 위치에 있는 가능한 타겟 찾기
            self.map_action.target_battler = None
            for target in self.map_action.level.battler_sprites:
                if target.pos == self.map_action.level.cursor.pos and target.team == self.map_action.selected_battler.team:
                    self.map_action.target_battler = target
                    break
                    
            if self.map_action.target_battler:
                self.map_action.current_dialog = ConfirmationDialog("사용하시겠습니까?")
                return
                    
            if self.map_action.target_battler:
                self.map_action.level.cursor.move_lock = True
                # 타일 제거
                self.map_action.highlight_tiles_set(None,mode='Clear')
                
                # 아이템 사용

                return 'interact','using_item1'
class Event_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
        self.message_dialog = None
        self.event_queue = []
        self.current_event = None
        
    def enter(self, event_queue, return_state):
        self.event_queue = event_queue
        self.return_state = return_state
        self.cursor.move_lock = True
        self.next_event()
    
    def next_event(self):
        if self.event_queue:
            next_message = self.event_queue.pop(0)
            self.message_dialog = MessageDialog([next_message], pygame.font.Font(GENERAL_FONT, 24), self.level)
        else:
            return self.return_state
            
    def update(self):
        if not self.message_dialog:
            return self.return_state
            
        self.message_dialog.update()
        self.message_dialog.render()
        
        if (self.map_action.input_manager.is_just_pressed('Select') or 
            self.map_action.input_manager.is_left_click()):
            if self.message_dialog and self.message_dialog.finished:
                self.message_dialog = None
                return self.next_event()
            elif self.message_dialog and not self.message_dialog.finished:
                self.message_dialog.finish_current_message()
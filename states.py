import pygame
from properties import *
from tile import Tile
from database import *
import random
from ui import ConfirmationDialog
from support import MessageDialog, Effect, EffectManager
from common_method import *
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
            battler.Cur_HP = int(battler.stats['Max_HP'])
            battler.Cur_MP = int(battler.stats['Max_MP'])
            self.map_action.effect_manager.update_effects(battler)
        self.map_action.current_phase = 'Init'
        self.map_action.change_state("phase_change")
        self.map_action.sound_manager.play_bgm(**SOUND_PROPERTIES['ALLY_PHASE'])
class Explore_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
    def enter(self):
        if event := self.event_check():
            return event
        
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
                self.map_action.timer('enemy_wait', 500)
                self.substate = 'Enemy_wait'
                return
            elif self.substate == 'Enemy_wait' and self.map_action.timer('enemy_wait'):
                self.substate = None
                return self.map_action.AI.execute()

    def event_check(self):
        if (not hasattr(self, 'event_triggered')
            and self.map_action.current_phase == 'Ally'
            and is_adjacent(next((b for b in self.level.battlers if b.char_type == 'Player1'), None), next((b for b in self.level.battlers if b.char_type == 'Player2'), None))):
            self.event_triggered = True
            return ('event', 'Event1', 'explore')
        elif (not hasattr(self, 'event_triggered2')
            and self.map_action.current_phase == 'Ally'
            and is_adjacent(next((b for b in self.level.battlers if b.char_type == 'Player2'), None), next((b for b in self.level.battlers if b.char_type == 'Player3'), None))):
            self.event_triggered2 = True
            return ('event', 'Event2', 'explore')
        if (not hasattr(self.map_action, 'spawn_order_2_triggered') or 
            not self.map_action.spawn_order_2_triggered):
            if self.map_action.death_count['Enemy'] >= 5:
                print("5명의 적을 처치했습니다! 새로운 적이 등장합니다!")
                self.level.spawn_battlers(2)  # spawn_order가 2인 배틀러들 소환
                self.map_action.spawn_order_2_triggered = True
                
                # 새로 소환된 배틀러들의 위치로 카메라 이동
                new_battlers = [b for b in self.level.battler_sprites 
                            if b.team == 'Enemy' and not b.inactive]
                if new_battlers:
                    self.level.visible_sprites.focus_on_target(new_battlers[0])
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
        self.map_action.selected_battler.inactive = False
        self.cursor.move_lock = False
        self.cursor.select_lock = False
        self.map_action.cur_moves = self.map_action.selected_battler.stats['Mov']
        self.map_action.level.visible_sprites.focus_on_target(self.map_action.selected_battler)
        self.map_action.highlight_tiles_set([pos[0] for pos in self.map_action.check_movable_from_pos(self.map_action.selected_battler.pos, self.map_action.cur_moves)], 'Update')
        # print(self.map_action.selected_battler.effects)
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
                    self.map_action.highlight_tiles_set([pos[0] for pos in self.map_action.check_movable_from_pos(pygame.math.Vector2(cursor_pos) // TILESIZE, self.map_action.cur_moves)], 'Update')
                    

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
            self.map_action.highlight_tiles_set([pos[0] for pos in self.map_action.check_movable_from_pos(self.map_action.selected_battler.pos, self.map_action.cur_moves)], 'Update')
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
            self.map_action.highlight_tiles_set([pos[0] for pos in self.map_action.check_movable_from_pos(last_root_pos, self.map_action.cur_moves)], 'Update')
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
                self.map_action.highlight_tiles_set([pos[0] for pos in self.map_action.check_movable_from_pos(pygame.math.Vector2(cursor_pos) // TILESIZE, self.map_action.cur_moves)], 'Update')
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
        if not self.map_action.selected_battler:
            # selected_battler가 None이면 explore 상태로 되돌아감
            return 'explore'

        self.cursor.move_lock = True
        self.cursor.SW_select = False
        self.map_action.selected_battler.isfollowing_root = True
        self.map_action.Acted.append([None,'Move'])

    def exit(self):
        if self.map_action.selected_battler:
            self.map_action.selected_battler.isfollowing_root = False

    def update(self):
        if not self.map_action.selected_battler:
            return 'explore'

        if not self.map_action.selected_battler.isacting:
            for battler in self.level.battler_sprites:
                if (battler != self.map_action.selected_battler and 
                    battler.pos == self.map_action.selected_battler.pos and 
                    battler.team == self.map_action.selected_battler.team and 
                    not battler in self.map_action.interacted_battlers):
                    self.map_action.interacted_battlers.append(battler)
                    self.support(battler)
           # 이동해야할 경로가 존재함.
            if self.map_action.move_roots:
                target_battlers = [battler for battler in self.level.battler_sprites 
                                if battler != self.map_action.selected_battler and 
                                battler not in self.map_action.interacted_battlers and 
                                battler.team != self.map_action.selected_battler.team]
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
    def support(self, battler):
        for skill_name, skill_level in battler.skills.items():
            skill_info = SKILL_PROPERTIES.get(skill_name, {})
            applied_effects = False
            is_support = skill_info.get('Passive').get('effect_type') if skill_info.get('Passive') else False
            if is_support == 'support':
                # print(skill_info)
                support = skill_info['Passive']['support']
                effects = skill_info['Passive']['effects']
                target = self.map_action.selected_battler if support.get('target') == 'passer' else battler
                effect_source = self.map_action.selected_battler if support.get('target') == 'effect_source' else battler
                animation = support.get('animation')
                if support['effect_type'] == 'buff':
                    if effects.get('stats'):
                        value = effects['stats'][skill_level]
                        effect = Effect(effect_type='supportbuff', effects=value, source=f"supportbuff_{skill_name}", remaining_turns=0)
                        self.map_action.effect_manager.add_effect(target, effect)
                        self.map_action.animation_manager.create_animation(target, animation, wait=True, track_target= True)
                    elif effects.get('stats_%'):
                        values = effects['stats_%'][skill_level]
                        value = {}
                        for key in values:
                            value.update({key : effect_source.stats[key] * values[key] / 100})
                        effect = Effect(effect_type='supportbuff', effects=value, source=f"supportbuff_{skill_name}", remaining_turns=0)
                        self.map_action.effect_manager.add_effect(target, effect)
                        self.map_action.animation_manager.create_animation(target, animation, wait=True, track_target= True)
                if support['effect_type'] == 'immediate':
                    if 'stats' in effects:
                        stat_effects = effects['stats'][skill_level]
                        for stat, value in stat_effects.items():
                            if stat == 'Cur_HP':
                                target.Cur_HP = min(target.stats['Max_HP'], target.Cur_HP + value)
                            elif stat == 'Cur_MP':
                                target.Cur_MP = min(target.stats['Max_MP'], target.Cur_MP + value)
                        if animation:
                            self.map_action.animation_manager.create_animation(target, animation, wait=True, track_target=True)
class Player_Menu_State(State):
    def enter(self, return_menu=None):  # return_menu 파라미터 추가
        self.level.ui.current_main_menu = return_menu if return_menu else 'main'  # return_menu가 있으면 해당 메뉴로, 없으면 'main'으로
        self.level.ui.selected_menu = 'init'
        self.cursor.move_lock = True
        self.map_action.highlight_tiles_set(None, mode='Clear')
    def update(self):
        command = self.level.ui.player_menu_control()
        if not command:
            return

        action = command[0]

        if action == '스킬타겟지정':
            self.map_action.skill = command[1]
            self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화
            return 'select_magic_target'
            
        elif action == '아이템사용':
            selected_item = command[1]
            self.map_action.item_to_use = selected_item
            self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화

            return 'select_item_target'
            
        elif action == '사격타겟지정':
            self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화
            return 'select_range_target'
            
        elif action == '대기':
            self.map_action.input_manager.reset_mouse_state()  # 배틀러 선택 후 마우스 상태 초기화
            self.map_action.endturn()
        
        elif action == '오버드라이브':
            self.map_action.skill = self.map_action.selected_battler.OVD_skill
            self.map_action.input_manager.reset_mouse_state()
            return 'select_magic_target'
            
        elif action == '취소':
            self.cursor.move_lock = False
            self.map_action.highlight_tiles_set([pos[0] for pos in self.map_action.check_movable_from_pos(self.map_action.selected_battler.pos, self.map_action.cur_moves)], 'Update')
            return 'player_control'
class Phase_Change_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
        self.substate = ''

    def enter(self):
        self.phase_order = []
        self.cursor.move_lock = True
        self.cursor.SW_select = False
        self.cursor.selected = False
        
        for team in self.map_action.base_phase_order:
            if [battler for battler in self.level.battler_sprites if battler.team == team]:
                self.phase_order.append(team)
                continue
        # print(self.phase_order)
        self.substate = 'change1'

    def update(self):
        if self.substate == 'change1':
            # 페이즈 전화 전 팀 효과 처리
            for battler in self.level.battler_sprites:
                if battler.team == self.map_action.current_phase:
                    self.map_action.effect_manager.elapse_turn(battler)
                    self.map_action.effect_manager.update_effects(battler)
                    
            if self.map_action.current_phase == 'Init':
                self.map_action.current_phase = 'Ally'
            else:
                self.map_action.current_phase = self.phase_order[(self.phase_order.index(self.map_action.current_phase) + 1) % len(self.phase_order)]
            # 페이즈 전환 후 팀 효과 처리
            for battler in self.level.battler_sprites:
                if battler.team == self.map_action.current_phase:
                    # HP/MP 회복 처리
                    status_effects = [effect for effect in battler.effects if effect.type == 'status']
                    # Turn 관련 카운터 증가
                    for key in battler.activate_condition:
                        if 'Turn' in key:
                            battler.activate_condition[key] += 1
                    self.map_action.effect_manager.update_effects(battler)
                    if battler.force_inactive:
                        battler.inactive = True
                    else:
                        battler.inactive = False
                    for effect in battler.effects:
                        if effect.type == 'buff_until_turn':
                            self.map_action.effect_manager.remove_effect(battler, effect_type=effect.type)

            if self.map_action.current_phase == 'Ally':
                phase_anim = self.map_action.animation_manager.create_animation(None,'PHASE_CHANGE',wait=True,value=[self.level.visible_sprites.offset, 'Player'])
                self.map_action.sound_manager.play_bgm(**SOUND_PROPERTIES['ALLY_PHASE'])
                self.map_action.elapsed_turn += 1
            elif self.map_action.current_phase == 'Enemy':
                phase_anim = self.map_action.animation_manager.create_animation(None,'PHASE_CHANGE',wait=True,value=[self.level.visible_sprites.offset, 'Enemy'])
                self.map_action.sound_manager.play_bgm(**SOUND_PROPERTIES['ENEMY_PHASE'])
            self.level.visible_sprites.focus_on_target([battler for battler in self.level.battler_sprites if battler.team == self.map_action.current_phase][0],cursor_obj=self.level.cursor)
            self.substate = 'change2'

        elif self.substate == 'change2' and not self.map_action.animation_manager.has_active_animations():
            if all(battler.inactive or battler.force_inactive 
                for battler in self.level.battler_sprites 
                if battler.team == self.map_action.current_phase):
                return 'phase_change'  # 바로 다음 페이즈로
            return 'explore'  # active한 배틀러가 있으면 explore로
class Interact_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
        self.substate = ''
    def enter(self,state= None):
        if state:
            self.substate = state        
        self.cursor.move_lock = True
        self.cursor.select_lock = True
    def exit(self):
        pass
    def update(self):
# - 기본 interact. 아군일 경우 힐(스킬보유시), 적군일 경우 공격
        if self.substate == 'contact':
            if (self.map_action.selected_battler.team == 'Ally' and self.map_action.target_battler.team == 'Enemy') or (
                  self.map_action.selected_battler.team == 'Enemy' and self.map_action.target_battler.team == 'Ally'):
                    
                char_data = CharacterDatabase.data.get(self.map_action.selected_battler.char_type, {})
                if char_data.get('Class') == 'Melee':
                    return 'interact','melee0'
                else:
                    return 'player_moving'
# - 데미지 계산 (_attack1) 및 ZOC 확인(발동 시 주변 타일로 이동)
        elif self.substate[:5] == 'melee':
            if self.substate == 'melee0':
                self.map_action.Acted.append([self.map_action.target_battler,'Melee'])
                self.map_action.selected_battler.isfollowing_root = False
                self.map_action.selected_battler.actlist.append('act_for_attack')
                self.map_action.timer('melee_attack0', self.map_action.selected_battler.attack_delay)
                return 'interact','melee1'

            elif self.substate == 'melee1' and self.map_action.timer('melee_attack0'):
                # 공격 효과 계산 및 적용
                attacker = self.map_action.selected_battler
                target = self.map_action.target_battler
                Damage_Bonus_multiplier, vurnerable = CombatFormulas.calculate_directional_bonus(attacker, target)

                # 카운터 확인
                if CombatFormulas.check_melee_counter(self,attacker, target, vurnerable):
                    self.map_action.animation_manager.create_animation(attacker.collision_rect.center, 'EMOTE_SURPRISE', wait=True)
                    target.battle_return(attacker, move_type='counter')
                    self.map_action.timer('melee_counter', self.map_action.selected_battler.attack_delay)
                    return 'interact','melee_counter1'
                    
                # 히트 체크
                if CombatFormulas.check_melee_evasion(self,attacker, target, vurnerable):
                    target.battle_return(attacker, move_type='evasion')
                    self.map_action.sound_manager.play_sound(**SOUND_PROPERTIES['EVASION'])
                    return 'interact','melee2'
                    
                # 크리티컬 확인
                if CombatFormulas.check_melee_critical(self,attacker, target, vurnerable):
                    is_critical = True
                    self.map_action.animation_manager.create_animation(target,'CRITICAL',wait=True)
                    self.map_action.level.visible_sprites.start_shake(0.3, intensity=10, direction='horizontal')

                else:
                    is_critical = False
                    
                damage = CombatFormulas.calculate_melee_damage(attacker, target, Damage_Bonus_multiplier, is_critical)
                self.map_action.animation_manager.create_animation(target,'SLASH',wait=True)
                target.battle_return(attacker, move_type='knockback')
                self.map_action.Damage(attacker, target, damage, "Melee", is_critical = is_critical)
                # ZOC 체크
                if CombatFormulas.check_ZOC(self,attacker, target, vurnerable, is_critical):
                    self.map_action.animation_manager.create_animation(target,'SHIELD2',wait=True)
                    # 이동 취소
                    while self.map_action.move_roots:
                        self.map_action.move_roots[-1][0].kill()
                        self.map_action.move_roots.pop()
                        
                    return 'interact','melee_ZOC1'
                    
                self.map_action.timer('melee_attack1', self.map_action.selected_battler.attack_delay)
                return 'interact','melee2'
    # - ZOC 발동 후 이동까지 대기 + 방어 애니메이션 완료까지 대기 (_attack_ZOC1)
            elif self.substate == 'melee_ZOC1' and not self.map_action.animation_manager.has_active_animations():
                # 안전한 타일 찾기
                gotopos = None
                i = 1
                if any(self.map_action.selected_battler.pos == battler.pos 
                    for battler in self.level.battler_sprites 
                    if battler != self.map_action.selected_battler):
                    while(not gotopos):
                        movable_tiles = self.map_action.check_movable_from_pos(self.map_action.selected_battler.pos,i)
                        for movable_tile in movable_tiles:
                            if all(movable_tile[0] != battler.pos 
                                for battler in self.level.battler_sprites 
                                if battler != self.map_action.selected_battler):
                                gotopos = movable_tile[0]
                                break
                        i += 1

                # 이동 적용
                if gotopos is not None:
                    self.map_action.selected_battler.Goto.x += (gotopos[0] * TILESIZE - self.map_action.selected_battler.return_tile_location()[0])
                    self.map_action.selected_battler.Goto.y += (gotopos[1] * TILESIZE - self.map_action.selected_battler.return_tile_location()[1])
                    self.map_action.selected_battler.ismove = True
                    self.map_action.selected_battler.pos = pygame.math.Vector2(gotopos[0], gotopos[1])

                return 'interact','melee_ZOC2'

            elif self.substate == 'melee_ZOC2' and not self.map_action.selected_battler.ismove:
                # 혼란 이모트 표시
                self.map_action.animation_manager.create_animation(self.map_action.selected_battler.collision_rect.center,'EMOTE_DESPAIR',wait=True)

                # ZOC 상태이상 적용
                status_chances = 0.2
                self.map_action.Acted.append([self.map_action.selected_battler,['status_여기어디_Check',CombatFormulas.ZOC_status_check()]])
                status = '여기어디'
                if random.random() < status_chances:
                    effect = Effect(effect_type='status',effects=STATUS_PROPERTIES[status].get('Stat', {}),source=f"status_{status}",remaining_turns=STATUS_PROPERTIES[status]['duration'])
                    self.map_action.selected_battler.effects.append(effect)
                    self.map_action.Acted.append([self.map_action.selected_battler,['status_여기어디_Check','Executed']])
                return 'interact','melee_ZOC3'

            elif self.substate == 'melee_ZOC3' and not self.map_action.animation_manager.has_active_animations():
                return 'interact','after_battle'

            elif self.substate == 'melee2' and self.map_action.timer('melee_attack1'):
                self.map_action.selected_battler.isfollowing_root = True
                return 'player_moving'

            elif self.substate == 'melee_counter1' and self.map_action.timer('melee_counter'):
                # 반격 데미지 계산
                counter_damage = CombatFormulas.calculate_melee_counter_damage(self,self.map_action.selected_battler, self.map_action.target_battler)

                # 애니메이션 생성
                self.map_action.animation_manager.create_animation(
                    (self.map_action.selected_battler.collision_rect.centerx, 
                    self.map_action.selected_battler.collision_rect.centery),
                    'SLASH',
                    wait=True
                )

                # 데미지 처리
                self.map_action.Damage(
                    self.map_action.target_battler,
                    self.map_action.selected_battler,
                    counter_damage,
                    "Melee"
                )

                # 이동 취소
                while self.map_action.move_roots:
                    self.map_action.move_roots[-1][0].kill()
                    self.map_action.move_roots.pop()

                # 후퇴 위치 찾기
                gotopos = None
                i = 1
                if any(self.map_action.selected_battler.pos == battler.pos 
                    for battler in self.level.battler_sprites 
                    if battler != self.map_action.selected_battler):
                    while(not gotopos):
                        movable_tiles = self.map_action.check_movable_from_pos(
                            self.map_action.selected_battler.pos,
                            i,
                            show=False
                        )
                        for movable_tile in movable_tiles:
                            if all(movable_tile[0] != battler.pos 
                                for battler in self.level.battler_sprites 
                                if battler != self.map_action.selected_battler):
                                gotopos = movable_tile[0]
                                break
                        i += 1

                if gotopos is not None:
                    # 후퇴 이동
                    self.map_action.selected_battler.Goto.x += (
                        gotopos[0] * TILESIZE - 
                        self.map_action.selected_battler.return_tile_location()[0]
                    )
                    self.map_action.selected_battler.Goto.y += (
                        gotopos[1] * TILESIZE - 
                        self.map_action.selected_battler.return_tile_location()[1]
                    )
                    self.map_action.selected_battler.ismove = True
                    self.map_action.selected_battler.pos = pygame.math.Vector2(gotopos[0], gotopos[1])

                return 'interact','melee_counter2'

            elif self.substate == 'melee_counter2' and not self.map_action.selected_battler.ismove:
                self.map_action.timer('melee_counter2', 1000)
                return 'interact','melee_counter3'

            elif self.substate == 'melee_counter3' and self.map_action.timer('melee_counter2'):
                self.level.visible_sprites.focus_on_target(self.map_action.selected_battler, cursor_obj=self.level.cursor)
                return 'interact','after_battle'
#   원거리 공격 처리
        elif self.substate[:5] == 'range':
            self.level.cursor.move_lock = True
            if self.substate == 'range0':
                self.map_action.Acted.append([self.map_action.target_battler,'Range'])
                self.level.cursor.move_lock = True
                self.map_action.highlight_tiles_set(None,mode='Clear')
                self.map_action.visible_sprites.focus_on_target(self.map_action.selected_battler)
                self.map_action.visible_sprites.enable_zoom()
                self.map_action.visible_sprites.zoom_to_battler(self.map_action.selected_battler)

                self.map_action.selected_battler.update_facing_direction(self.map_action.target_battler.pos - self.map_action.selected_battler.pos)
                self.map_action.selected_battler.actlist.append('range_attack')
                self.map_action.sound_manager.play_sound(**SOUND_PROPERTIES['ARROW_FLYING'])   
                self.map_action.sound_manager.play_sound(**SOUND_PROPERTIES['SHOOT_ARROW'])   

                self.map_action.timer('melee_range', 500)
                return 'interact','range1'

            elif self.substate == 'range1' and self.map_action.timer('melee_range'):
                self.level.visible_sprites.focus_on_target(self.map_action.target_battler)
                self.map_action.timer('melee_range1', 500)
                return 'interact','range2'

            elif self.substate == 'range2' and self.map_action.timer('melee_range1'):
                attacker = self.map_action.selected_battler
                target = self.map_action.target_battler

                # 명중 판정
                if CombatFormulas.check_range_evasion(self,attacker, target):
                    target.battle_return(attacker, move_type='range_evasion')
                    self.map_action.sound_manager.play_sound(**SOUND_PROPERTIES['EVASION'])
                else:
                    is_critical = False
                    if CombatFormulas.check_range_critical(self,attacker, target):
                        is_critical = True
                        self.map_action.animation_manager.create_animation((target.collision_rect.centerx, target.collision_rect.centery),'CRITICAL',wait=True)
                    damage = CombatFormulas.calculate_range_damage(attacker, target, is_critical)
                    self.map_action.Acted.append([target,'Range_Damage',damage])
                    self.map_action.animation_manager.create_animation(target.collision_rect.center,'RANGE_HIT',wait=True)
                    target.battle_return(attacker, move_type='knockback')
                    # 데미지 적용
                    self.map_action.Damage(attacker, target, damage, "Range",is_critical=is_critical)
                self.map_action.timer('melee_range2', 500)
                return 'interact','range3'

            elif self.substate == 'range3' and self.map_action.timer('melee_range2'):
                self.level.visible_sprites.focus_on_target(self.map_action.selected_battler, cursor_obj=self.level.cursor)
                return 'interact','after_battle'
#   스킬 애니메이션 생성 처리(_skill), 배틀러가 행동(casting)을 마무리할 때 처리 시작
        elif self.substate[:5] == 'skill':
            attacker = self.map_action.selected_battler
            skill_name = self.map_action.skill
            skill_info = SKILL_PROPERTIES[skill_name]['Active']
            if skill_info['type'] == 'overdrive':
                skill_level = attacker.OVD_level
            elif skill_info['type'] in  ['magic','skill']:
                skill_level = attacker.skills[skill_name]
                
            if self.substate == 'skill0':
                # MP 소모
                skill_mana = skill_info.get('mp_cost',{}).get(skill_level, 0)
                attacker.Cur_MP -= skill_mana

                # 시전한 게 스킬인지 마법인지 확인
                if skill_info['type'] == 'magic':
                    self.map_action.Acted.append([None,'Magic_Casting',[skill_name,skill_level]])
                elif skill_info['type'] == 'skill':
                    self.map_action.Acted.append([None,'Use_Skill',[skill_name,skill_level]])
                elif skill_info['type'] == 'overdrive':
                    self.map_action.Acted.append([None,'Overdrive',[skill_name,skill_level]])

                else:
                    print(f'Error: 타입 인식 실패 : {skill_info["type"]}')
                # 방향 설정 및 캐스팅 시작
                attacker.update_facing_direction(self.level.cursor.pos - attacker.pos)
                attacker.actlist.append('casting')
                attacker.selected = False

                # 스킬 캐스팅 설정
                self.level.visible_sprites.focus_on_target(attacker,self.level.cursor)
                self.level.cursor.move_lock = True
                self.level.cursor.SW_select = True
                
                # 줌 효과
                self.map_action.visible_sprites.enable_zoom()
                self.map_action.visible_sprites.zoom_to_battler(attacker)

                # 캐스팅 애니메이션
                if skill_info['cast_animation']:
                    self.map_action.animation_manager.create_animation((attacker.return_tile_location()[0],attacker.return_tile_location()[1] - TILESIZE),skill_info['cast_animation'],wait=True)

                self.substate = 'skill1'

            elif self.substate == 'skill1' and not self.map_action.selected_battler.isacting:
                self.map_action.visible_sprites.disable_zoom()
                
                targets = ([self.map_action.target_battler] if not isinstance(self.map_action.target_battler, list) else self.map_action.target_battler)
                
                if targets:
                    first_target = targets[0]
                    self.level.visible_sprites.focus_on_target(first_target)
                
                skill_info = SKILL_PROPERTIES[self.map_action.skill]['Active']
                if skill_info['type'] == 'overdrive':
                    skill_level = self.map_action.selected_battler.OVD_level
                elif skill_info['type'] in  ['magic','skill']:
                    skill_level = self.map_action.selected_battler.skills[self.map_action.skill]
                animate_type = skill_info.get('animate_type', None)
                
                if animate_type == 'sequential':
                    # 타일 위치들을 거리 순으로 정렬
                    tile_positions = [tile for tile in self.map_action.highlight_tiles]
                    tile_positions.sort(key=lambda tile: (
                        abs(tile.pos.x - self.map_action.selected_battler.pos.x) + 
                        abs(tile.pos.y - self.map_action.selected_battler.pos.y)
                    ))
                    
                    # 첫 번째 타일에 대한 애니메이션
                    if tile_positions:
                        self.map_action.animation_manager.create_animation(tile_positions[0],skill_info.get('effect_animation', 'SLASH'),wait=True)
                        # 첫 번째 타일에 있는 대상에게 데미지
                        for target in targets:
                            if target.pos == tile_positions[0].pos:
                                self.map_action.apply_skill_effects(target,self.map_action.skill,skill_level) 
                    self.sequence_tiles = tile_positions[1:]
                    self.sequence_delay = skill_info['sequential']['tick']
                    self.map_action.timer('skill_sequence', self.sequence_delay * 1000)
                    return 'interact', 'skill_sequence'
                    
                elif animate_type == 'all_tiles':
                    # 모든 타일에 동시에 애니메이션
                    for tile in self.map_action.highlight_tiles:
                        self.map_action.animation_manager.create_animation((tile.rect.midtop[0], tile.rect.midtop[1]),skill_info.get('effect_animation', 'SLASH'),wait=True)
                        
                elif animate_type == 'default':  # default나 battler 타입
                    # 각 대상별로 애니메이션
                    for target in targets:
                        self.map_action.animation_manager.create_animation((target.collision_rect.midtop[0], target.collision_rect.midtop[1]),skill_info.get('effect_animation', 'SLASH'),wait=True)
                elif animate_type == 'target':
                    self.map_action.animation_manager.create_animation(self.map_action.animate_pos,skill_info.get('effect_animation', 'SLASH'),wait=True)
                else:
                    print(f'Error: 애니메이션 타입 인식 실패 : {animate_type}')
                    
                self.map_action.timer('melee_skill1', skill_info.get('Dmg_timing', 0))
                return 'interact', 'skill2'
                
            elif self.substate == 'skill2' and self.map_action.timer('melee_skill1'):
                targets = (self.map_action.target_battler if isinstance(self.map_action.target_battler, list) else [self.map_action.target_battler])
                
                for target in targets:
                    self.map_action.apply_skill_effects(target,self.map_action.skill,skill_level)
                    
                return 'interact', 'skill3'
                
            elif self.substate == 'skill3' and not self.map_action.animation_manager.has_active_animations():
                    self.map_action.highlight_tiles_set(None, mode='Clear')
                    # 시전자에게 다시 포커스
                    self.level.visible_sprites.focus_on_target(self.map_action.selected_battler,self.level.cursor)
                    return 'interact', 'after_battle'
                
            elif self.substate == 'skill_sequence':
                if self.map_action.timer('skill_sequence') and self.sequence_tiles:
                    # 다음 타일 애니메이션 생성
                    skill_info = SKILL_PROPERTIES[self.map_action.skill]['Active']
                    tile = self.sequence_tiles.pop(0)
                    self.map_action.animation_manager.create_animation(tile,skill_info.get('effect_animation', 'SLASH'),wait=True)
                    
                    # 해당 타일에 있는 타겟에게 데미지
                    targets = (self.map_action.target_battler 
                            if isinstance(self.map_action.target_battler, list) 
                            else [self.map_action.target_battler])
                            
                    for target in targets:
                        if target.pos == tile.pos:
                            self.map_action.apply_skill_effects(target,self.map_action.skill,skill_level)
                    
                    if self.sequence_tiles:
                        self.map_action.timer('skill_sequence', self.sequence_delay * 1000)
                    else:
                        return 'interact', 'skill3'
#   배틀 종료 후 사망 여부 판정 (_interact_after_battle)
        elif self.substate[:12] == 'after_battle':
            if self.substate == 'after_battle':
                self.map_action.process_exp_gain()
                self.map_action.process_OVD_gain()
                self.map_action.visible_sprites.disable_zoom()
                if any(battler.Cur_HP == 0 for battler in self.level.battler_sprites):
                    self.map_action.timer('after_battle', 500)
                    return 'interact','after_battle_death1'
    #   아무것도 사망하지 않으면 캐릭터 턴 종료
                else:
                    self.map_action.endturn()

            elif self.substate == 'after_battle_death1' and self.map_action.timer('after_battle'):
                for battler in self.level.battler_sprites:
                    if battler.Cur_HP == 0:
                        self.map_action.death_count[battler.team] += 1
                        # 경험치 획득 및 레벨업 처리
                        battler.death()  # 예시: 배틀러를 죽이는 메서드 호출
                return 'interact','after_battle_death2'           
#   사망한 배틀러가 존재할 시 해당 배틀러들이 isdead를 띄울 때까지 대기, 이 후 객체 kill (_interact_death)
            elif self.substate == 'after_battle_death2' and all((battler.Cur_HP <= 0 and battler.isdead) or battler.Cur_HP > 0 for battler in self.level.battler_sprites):
                # for battler in self.level.battler_sprites:
                #     if battler.Cur_HP <= 0:
                        
                #         battler.kill()
                self.map_action.timer('after_battle_death2', 1000)
                return 'interact','after_battle_death3'

            elif self.substate == 'after_battle_death3' and self.map_action.timer('after_battle_death2'):
                self.map_action.endturn()

        elif self.substate[:10] == 'using_item':
            if self.substate == 'using_item1':
                item_data = ITEM_PROPERTIES[self.map_action.item_to_use]
                if 'animate' in item_data:
                    self.map_action.animation_manager.create_animation(self.map_action.target_battler,item_data['animate'],wait=True)
                return 'interact','using_item2' 
            elif self.substate == 'using_item2' and not self.map_action.animation_manager.has_active_animations():
                self.map_action.timer('using_item2', 300)
                return 'interact','using_item3'
            elif self.substate == 'using_item3' and self.map_action.timer('using_item2'):
                self.map_action.use_item(self.map_action.target_battler, self.map_action.item_to_use)
                self.map_action.timer('using_item3', 800)
                return 'interact','using_item4'
            elif self.substate == 'using_item4' and self.map_action.timer('using_item3'):
                self.level.ui.current_item_menu_index = 0
                self.map_action.endturn()
class Select_Magic_Target_State(State):
    def enter(self, state = None):
        self.map_action.temp_facing = self.map_action.selected_battler.facing  # 임시 방향 초기화
        attackable_pos = self.map_action.check_magic_range(self.map_action.selected_battler,self.map_action.skill)
        self.level.cursor.move_lock = False
        self.level.cursor.SW_select = False
        self.level.cursor.select_lock = True
        self.map_action.highlight_tiles_set(None,mode = 'All_Clear')
        self.map_action.highlight_tiles_set([pygame.math.Vector2(x,y)for x , y in attackable_pos], mode = 'Set')
        # 자신에게 시전이면 즉시 시전.
        if ['Self'] == SKILL_PROPERTIES[self.map_action.skill]['Active']['target_team']:
            self.map_action.target_battler = self.map_action.selected_battler
            self.map_action.current_dialog = ConfirmationDialog("사용하시겠습니까?")
    def update(self):
        # 대화상자 처리
        skill_info = SKILL_PROPERTIES[self.map_action.skill]['Active']
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
                        return 'interact','skill0'
                else:
                    self.level.cursor.move_lock = False  # 커서 이동 잠금 해제
                    self.map_action.target_battler = None
                    if ['Self'] == skill_info['target_team']:
                        self.map_action.current_dialog = None
                        self.map_action.target_battler = None
                        self.level.ui.current_main_menu = 'skill'
                        return 'player_menu', 'skill'
                self.map_action.current_dialog = None
            return
        # 직선형 스킬일 때 방향 변경 처리
        if skill_info.get('range_type') == 'linear':
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
            
            # 방향이 바뀌었다면 해당 방향으로 타일 재생성
            if new_facing and new_facing != self.map_action.temp_facing:
                self.map_action.temp_facing = new_facing
                self.map_action.highlight_tiles_set(None,mode='Clear')
                attackable_pos = self.map_action.check_magic_range(self.map_action.selected_battler,self.map_action.skill)
                self.map_action.highlight_tiles_set([pygame.math.Vector2(x,y)for x , y in attackable_pos], mode = 'Set')
        elif skill_info.get('target_option') == 'part':
            attackable_area = self.map_action.check_magic_area(self.map_action.selected_battler,self.map_action.skill,self.cursor)
            self.map_action.highlight_tiles_set(None,mode = 'Clear',identifier = 'area')
            self.map_action.highlight_tiles_set([pygame.math.Vector2(x,y)for x , y in attackable_area], mode = 'Set',identifier = 'area', color = 'red')
        
        if self.map_action.input_manager.is_just_pressed('Cancel'):
            self.map_action.temp_facing = self.map_action.selected_battler.facing  # 원래 방향 복원 
            self.level.visible_sprites.focus_on_target(self.map_action.selected_battler,cursor_obj=self.level.cursor)
            self.level.cursor.move_lock = True
            self.level.cursor.SW_select = True 
            self.level.cursor.select_lock = False
            tmp_skill = self.map_action.skill
            self.map_action.skill = None
            if SKILL_PROPERTIES[tmp_skill]['Active'].get('type') in ['skill','magic']:
                self.map_action.highlight_tiles_set(None,mode='All_Clear')
                return ('player_menu', 'skill')  # 튜플로 상태와 메뉴 데이터 전달
            elif SKILL_PROPERTIES[tmp_skill]['Active'].get('type') == 'overdrive':
                self.map_action.highlight_tiles_set(None,mode='All_Clear')
                return ('player_menu', 'skill')
        if (self.map_action.input_manager.is_just_pressed('Select') or self.level.cursor.clicked_self):
            if self.level.cursor.clicked_self:
                self.level.cursor.clicked_self = False
            target_option = skill_info.get('target_option', {})
            # 강조된 타일 위에 커서가 올려졌을 때 조건문 실행
            if any(self.level.cursor.pos == pygame.math.Vector2(attackable_tile.rect.topleft[0] // TILESIZE, attackable_tile.rect.topleft[1] // TILESIZE) for attackable_tile in self.map_action.highlight_tiles if getattr(attackable_tile, 'identifier', '') == ''):
                # 단일 타게팅 
                if target_option == 'one':      # 범위 내 단일 타게팅
                    self.map_action.target_battler = None
                    for battler in self.level.battler_sprites:
                        if self.level.cursor.pos == battler.pos and istarget(self.map_action.skill,self.map_action.selected_battler,battler):
                            self.map_action.target_battler = battler
                            break
                # 범위 타게팅 수정
                elif target_option == 'all':    # 범위 내 모든 배틀러 타게팅
                    self.map_action.target_battler = []
                    skill_area = [tile.pos for tile in self.map_action.highlight_tiles]
                    for battler in self.level.battler_sprites:
                        if battler.pos in skill_area:
                            if istarget(self.map_action.skill,self.map_action.selected_battler,battler):
                                self.map_action.target_battler.append(battler)
                elif target_option == 'part':   # 범위 내 일부 타게팅
                    self.map_action.target_battler = []
                    area = [tile.pos for tile in self.map_action.highlight_tiles if tile.identifier == 'area']
                    for battler in self.level.battler_sprites:
                        if battler.pos in area:
                            if istarget(self.map_action.skill,self.map_action.selected_battler,battler):
                                self.map_action.target_battler.append(battler)
                # 타겟이 있으면 확인 대화상자 표시
                if self.map_action.target_battler:
                    self.map_action.animate_pos = self.cursor.rect.center
                    self.level.cursor.move_lock = True
                    self.level.cursor.select_lock = True
                    self.map_action.current_dialog = ConfirmationDialog("사용하시겠습니까?")
class Select_Range_Target_State(State):
    def enter(self):
        self.cursor.move_lock = False
        attack_range = CharacterDatabase.data.get(self.map_action.selected_battler.char_type, {}).get('Range')
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
                    # 타일 제거
                    self.map_action.highlight_tiles_set(None,mode='Clear')
                    # 아이템 사용
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
class Event_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
        self.message_dialog = None
        self.event_queue = []
        self.current_event = None
        self.focus_queue = []
        self.focus_timer = None
        self.focus_duration = 1000  # 1 second per focus
        self.current_phase = 'dialog'  # 'dialog', 'focus', 'complete'

    def display_text(self, text):
        """Display text in message dialog"""
        self.message_dialog = MessageDialog([text], pygame.font.Font(GENERAL_FONT, 24), self.level)
        self.current_phase = 'dialog'
        return None

    def spawn_queue(self, spawn_order):
        """Spawn enemies and set up focus queue"""
        # Spawn new enemies
        self.level.spawn_battlers(spawn_order)
        self.map_action.spawn_order_2_triggered = True
        
        # Set up focus queue
        self.focus_queue = [b for b in self.level.battler_sprites 
                          if b.team == 'Enemy' and not b.inactive]
        
        # Add original battler to focus at the end
        original_battler = next((b for b in self.level.battlers 
                               if b.team == 'Ally' and not b.inactive), None)
        if original_battler:
            self.focus_queue.append(original_battler)
            
        # Start focus timer
        self.focus_timer = pygame.time.get_ticks()
        self.current_focus = 0
        self.current_phase = 'focus'
        return None

    def enter(self, event_queue, return_state):
        Event_List = {
            "Event1": [
                lambda: self.display_text("이벤트1입니다. Player1과 Player2가 근접했을 경우 실행됩니다."),
                lambda: self.display_text("이렇게 긴 메세지는 출력되기 전에 Cancel 키를 누르면 즉시 출력을 할 수 있습니다.")
            ],
            "Event2": [
                lambda: self.display_text("이벤트2입니다. Player2와 Player3이 근접했을 경우 실행됩니다."),
                lambda: self.display_text("이렇게 긴 메세지는 출력되기 전에 Cancel 키를 누르면 즉시 출력을 할 수 있습니다.")
            ],
            "Reinforcement": [
                lambda: self.display_text("5명의 적을 처치했습니다! 새로운 적이 등장합니다!"),
                lambda: self.spawn_queue(2)
            ]
        }
        
        self.return_state = return_state
        self.cursor.move_lock = True
        
        if event_queue in Event_List:
            self.event_queue = Event_List[event_queue].copy()
            self.execute_next_event()

    def execute_next_event(self):
        """Execute the next event in queue"""
        if self.event_queue:
            next_event = self.event_queue.pop(0)
            next_event()
        else:
            return self.return_state
        return None

    def update(self):
        if self.current_phase == 'focus':
            current_time = pygame.time.get_ticks()
            if current_time - self.focus_timer >= self.focus_duration:
                self.focus_timer = current_time
                self.current_focus += 1
                
                if self.current_focus < len(self.focus_queue):
                    # Focus on next battler
                    self.level.visible_sprites.focus_on_target(
                        self.focus_queue[self.current_focus]
                    )
                else:
                    # Finished focusing on all battlers
                    self.focus_queue = []
                    return self.execute_next_event()
            return None

        elif self.current_phase == 'dialog':
            if self.message_dialog:
                self.message_dialog.update()
                self.message_dialog.render()
                
                # Handle instant display with Cancel
                if self.map_action.input_manager.is_just_pressed('Cancel'):
                    if not self.message_dialog.finished:
                        self.message_dialog.finish_current_message()
                        return None
                        
                # Handle dialog completion
                if ((self.map_action.input_manager.is_just_pressed('Select') or 
                     self.map_action.input_manager.is_left_click()) and 
                    self.message_dialog.finished):
                    self.message_dialog = None
                    return self.execute_next_event()
            
        return None
class Upgrade_State(State):
    def __init__(self, map_action):
        super().__init__(map_action)
        
    def enter(self):
        self.cursor.move_lock = True
        self.cursor.SW_select = False
        self.map_action.selected_battler.selected = False
        self.map_action.level.visible_sprites.focus_on_target(self.map_action.selected_battler)

        self.overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 180))
        
        self.font = pygame.font.Font(UI_FONT, 36)
        self.title = self.font.render("레벨 업!", True, (255, 255, 255))
        self.title_rect = self.title.get_rect(center=(WIDTH//2, 100))

        # Draw 3 cards based on rarity probability
        self.cards = []
        for _ in range(3):
            if random.random() < 0.8:  # 80% Common
                card = random.choice(CARD_PROPERTIES['Common'])
            else:  # 20% Uncommon
                card = random.choice(CARD_PROPERTIES['Uncommon'])
            self.cards.append(card)

        
        self.selected_card = 0
        self.card_width = 256
        self.card_height = 384
        self.card_spacing = 32
        self.total_width = (self.card_width * 3) + (self.card_spacing * 2)
        self.start_x = (WIDTH - self.total_width) // 2
        self.start_y = HEIGHT//2 - self.card_height//2

        # Arrow properties
        self.arrow_height = 30
        self.arrow_width = 40
        self.arrow_y = self.start_y + self.card_height + 20

    def draw_arrow(self, x):
        points = [
            (x, self.arrow_y),
            (x - self.arrow_width//2, self.arrow_y + self.arrow_height),
            (x + self.arrow_width//2, self.arrow_y + self.arrow_height)
        ]
        pygame.draw.polygon(self.display_surface, (255, 255, 255), points)

    def draw_card(self, card, x, y, is_selected):
        card_rect = pygame.Rect(x, y, self.card_width, self.card_height)
        bg_color = (64, 64, 96) if is_selected else (32, 32, 48)
        pygame.draw.rect(self.display_surface, bg_color, card_rect, border_radius=10)
        pygame.draw.rect(self.display_surface, (100, 100, 150), card_rect, 2, border_radius=10)

        title_font = pygame.font.Font(UI_FONT, 24)
        title_surf = title_font.render(card["title"], True, (255, 255, 255))
        title_rect = title_surf.get_rect(midtop=(x + self.card_width//2, y + 24))
        self.display_surface.blit(title_surf, title_rect)

        desc_font = pygame.font.Font(UI_FONT, 18)
        desc_lines = card["desc"].split('\n')
        for i, line in enumerate(desc_lines):
            desc_surf = desc_font.render(line, True, (200, 200, 200))
            desc_rect = desc_surf.get_rect(midtop=(x + self.card_width//2, title_rect.bottom + 24 + i*24))
            self.display_surface.blit(desc_surf, desc_rect)

        return card_rect

    def update(self):
        if self.map_action.animation_manager.has_active_animations():
            print("wait!")
            return
        self.display_surface = pygame.display.get_surface()
        mouse_pos = self.map_action.input_manager.get_mouse_pos()
        
        self.display_surface.blit(self.overlay, (0, 0))
        self.display_surface.blit(self.title, self.title_rect)
        
        # Handle keyboard input
        if self.map_action.input_manager.is_just_pressed('Left') and self.selected_card > 0:
            self.selected_card -= 1
        elif self.map_action.input_manager.is_just_pressed('Right') and self.selected_card < 2:
            self.selected_card += 1
            
        for i, card in enumerate(self.cards):
            card_x = self.start_x + (self.card_width + self.card_spacing) * i
            card_rect = pygame.Rect(card_x, self.start_y, self.card_width, self.card_height)
            
            # Card is highlighted if mouse hovers over it or if it's selected with keyboard
            is_highlighted = card_rect.collidepoint(mouse_pos) or i == self.selected_card
            self.draw_card(card, card_x, self.start_y, is_highlighted)
            
            if i == self.selected_card:
                self.draw_arrow(card_x + self.card_width//2)
            
            if (card_rect.collidepoint(mouse_pos) and self.map_action.input_manager.is_left_click()) or \
                (i == self.selected_card and self.map_action.input_manager.is_just_pressed('Select')):
                self.apply_upgrade(i)
                self.map_action.endturn()

    def apply_upgrade(self, card_index):
        battler = self.map_action.selected_battler
        card = self.cards[card_index]
        
        # Apply skill upgrades 
        for skill_name, level in card['act']['skill'].items():
            if skill_name in battler.skills:
                battler.skills[skill_name] += level
            else:
                battler.skills[skill_name] = level
        
        # Remove all existing passive/equipment effects
        battler.effects = [effect for effect in battler.effects 
                          if effect.type not in ['supportbuff', 'equipment', 'passive']]
        
        # Reapply all passive skills effects
        for skill_name, skill_level in battler.skills.items():
            if skill_info := SKILL_PROPERTIES.get(skill_name, {}).get('Passive'):
                if skill_info.get('condition'):
                    # Condition-based passive skills will be checked by effect manager
                    continue
                    
                if effects := skill_info.get('effects'):
                    if 'stats' in effects:
                        value = effects['stats'][skill_level]
                    elif 'stats_%' in effects:
                        value = {}
                        values = effects['stats_%'][skill_level]
                        for key in values:
                            value[key] = battler.stats[key] * values[key] / 100
                        
                    effect = Effect(
                        effect_type='passive',
                        effects=value,
                        source=f"passive_{skill_name}",
                        remaining_turns=0
                    )
                    battler.effects.append(effect)
                    
        # Reapply equipment effects
        if hasattr(battler, 'equipment'):
            for slot, item in battler.equipment.items():
                if item and 'stats' in item:
                    effect = Effect(
                        effect_type='equipment',
                        effects=item['stats'],
                        source=f"equipment_{slot}",
                        remaining_turns=0
                    )
                    battler.effects.append(effect)
                    
        battler.upgrade_points -= 1
        self.map_action.effect_manager.update_effects(battler)
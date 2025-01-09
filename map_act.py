# map_act.py
import pygame
from properties import *
from tile import Tile
from database import *
from collections import deque
import random
from support import SoundManager, InputManager, EffectManager, Effect
from ai import AI
from ui import ConfirmationDialog
from states import *

class MapAction:
    def __init__(self,level_instance):
        self.level = level_instance
        self.animation_manager = level_instance.animation_manager
        self.visible_sprites = self.level.visible_sprites
        self.obstacle_sprites = self.level.obstacle_sprites
        self.current_phase = 'Ally'
        self.base_phase_order = ['Ally', 'Supporter', 'Enemy','Neutral','Non-Player','Visitor']
        self.neutral_mode = ''
        self.previous_mode = ''
        self.current_mode = 'init'
        self.states = {
            "init": InitState(self),
            "explore": Explore_State(self),
            "look_object": Look_Object_State(self),
            "player_control": Player_Control_State(self),
            "player_moving": Player_Moving_State(self),
            "player_menu": Player_Menu_State(self),
            "phase_change": Phase_Change_State(self),
            "interact": Interact_State(self),
            "select_magic_target": Select_Magic_Target_State(self),
            "select_range_target": Select_Range_Target_State(self),
            "select_item_target": Select_Item_Target_State(self),
            "event": Event_State(self),
        }
        self.current_state = self.states["init"]
        self.move_roots = []
        self.cur_moves = 0
        self.selected_battler = None
        self.interacted_battlers = []
        self.target_battler = None
        self.input_manager = InputManager()  # input_manager로 이름 변경
        self.sound_manager = SoundManager()
        self.effect_manager = EffectManager()
        self.AI = AI(self)
        self.update_time = 0
        self.step_enemy_turns = False
        self.movable_tiles = []
        self.highlight_tiles = []
        self.current_skill_index = 0  # 선택된 스킬 인덱스 추가
        self.Acted = []
        self.battle_exp_gain = 0
        self.current_dialog = None
        self.path_dragging = False
        self.last_drag_pos = None
        self.temp_facing = ''
        self.elapsed_turn = 0
        # 초기 BGM 재생

    def change_state(self, new_state):
        if isinstance(new_state, tuple):
            state_name, *state_data = new_state
        else:
            state_name = new_state
            state_data = None

        if state_name in self.states:
            self.current_state.exit()
            self.current_state = self.states[state_name]
            if state_data:
                state = self.current_state.enter(*state_data)  # 데이터와 함께 상태 진입
            else:
                state = self.current_state.enter()
            if state:
                self.change_state(state)
        else:
            print(f"상태 {state_name}는 존재하지 않습니다. 데이터 : {state_data}")

    def update(self):
        state = self.current_state.update()
        if state:
            self.change_state(state)
##### 경험치 습득 및 레벨업 처리
    def process_exp_gain(self):
        """경험치 획득과 레벨업 처리"""
        for battler in self.level.battler_sprites:
            if battler.tmp_exp_gain:
                # 경험치 획득량 계산 (CHA와 EXP 배율 적용)
                exp_gain = battler.tmp_exp_gain * (1 + 0.01 * battler.stats["CHA"]) * battler.stats["EXP_multiplier"]
                battler.exp += exp_gain
                battler.tmp_exp_gain = 0
                
                # 레벨업 체크
                while battler.exp >= battler.stats['Max_EXP']:
                    # 초과 경험치 계산
                    excess_exp = battler.exp - battler.stats['Max_EXP']
                    
                    # 레벨업
                    battler.LV += 1
                    
                    # 새로운 스탯 계산
                    new_stats = CharacterDatabase.calculate_stats(battler.char_type, battler.LV)
                    
                    # HP, MP 회복 처리 (레벨업 리젠 포함)
                    hp_heal = (new_stats["Max_HP"] - battler.stats['Max_HP'] + 
                            battler.stats["Level_Up_Regen"] * new_stats["Max_HP"])
                    mp_heal = (new_stats["Max_MP"] - battler.stats['Max_MP'] + 
                            battler.stats["Level_Up_Regen"] * new_stats["Max_MP"])
                            
                    battler.Cur_HP = min(battler.Cur_HP + hp_heal, new_stats["Max_HP"])
                    battler.Cur_MP = min(battler.Cur_MP + mp_heal, new_stats["Max_MP"])
                    
                    # 기본 스탯 업데이트하고 효과 재계산
                    battler.base_stats = new_stats.copy()
                    self.effect_manager.update_effects(battler)
                    
                    # 초과 경험치 이전
                    battler.exp = excess_exp
                    
                    # 레벨업 애니메이션
                    self.animation_manager.create_animation(battler, 'LEVEL_UP')
                    self.animation_manager.create_animation(battler, 'AURA')
       
    def use_item(self, battler, item_name):
        """아이템 사용 처리"""
        if item_name not in self.selected_battler.inventory:
            return False
            
        item_data = ITEM_PROPERTIES[item_name]
        effect_data = item_data['Effect']
        
        # 퍼센트 기반 힐링
        if 'Heal_%' in effect_data:
            for stat, value in effect_data['Heal_%'].items():
                if stat == 'Cur_HP':
                    heal_amount = int(battler.stats['Max_HP'] * value / 100)
                    battler.Cur_HP = min(battler.stats['Max_HP'], battler.Cur_HP + heal_amount)
                    self.animation_manager.create_animation(
                        (battler.collision_rect.centerx, battler.collision_rect.top - 10),
                        'DAMAGE',
                        value=heal_amount
                    )
                elif stat == 'Cur_MP':
                    heal_amount = int(battler.stats['Max_MP'] * value / 100)
                    battler.Cur_MP = min(battler.stats['Max_MP'], battler.Cur_MP + heal_amount)
                    
        # 고정값 힐링
        elif 'Heal' in effect_data:
            for stat, value in effect_data['Heal'].items():
                if stat == 'Cur_HP':
                    battler.Cur_HP = min(battler.stats['Max_HP'], battler.Cur_HP + value)
                    self.animation_manager.create_animation(
                        (battler.collision_rect.centerx, battler.collision_rect.top - 10),
                        'DAMAGE',
                        value=value
                    )
                elif stat == 'Cur_MP':
                    battler.Cur_MP = min(battler.stats['Max_MP'], battler.Cur_MP + value)
        
        # 버프 효과 적용
        duration = effect_data.get('duration', None)
        
        # 퍼센트 효과가 있다면
        if 'Buff_%' in effect_data:
            effect = Effect(
                effect_type='item_buff',
                effects=effect_data['Buff_%'],
                source=f"item_{item_name}_percent",
                remaining_turns=duration,
                is_percent=True
            )
            self.effect_manager.add_effect(battler, effect)
        
        # 고정값 효과가 있다면
        if 'Buff' in effect_data:
            effect = Effect(
                effect_type='item_buff',
                effects=effect_data['Buff'],
                source=f"item_{item_name}",
                remaining_turns=duration
            )
            self.effect_manager.add_effect(battler, effect)
        
       # 영구 Change 효과가 있다면
        if 'Change' in effect_data:
            effect = Effect(
                effect_type='change',
                effects=effect_data['Change'],
                source=f"change_{item_name}",
                remaining_turns=None  # 영구 지속
            )
            self.effect_manager.add_effect(battler, effect)
        
        # 인벤토리에서 아이템 제거
        self.selected_battler.inventory.remove(item_name)
        

        
        return True

    def update_path_tiles(self):
        """이동 경로 업데이트"""
        Tile.update_path_tiles(self.move_roots, self.visible_sprites, self.obstacle_sprites, self.selected_battler)

    def check_movable_from_pos(self, start_pos, moves_left, show=True, check_pos=None, exclude_pos=[], except_self=False):
        """특정 위치에서의 이동 가능 범위 계산"""
        self.highlight_tiles_set(None,mode='Clear')
        moves_data = self.level.level_data["moves"]
        visited = {}
        movable_positions = []
        paths = {}
        if not except_self:
            character_pos_tuple = (float(self.selected_battler.pos.x), float(self.selected_battler.pos.y))
        else:
            character_pos_tuple = ()
        start_pos_tuple = (float(start_pos.x), float(start_pos.y))
        
        queue = deque([(start_pos, 0, [start_pos_tuple])])

        visited[start_pos_tuple] = 0
        paths[start_pos_tuple] = {tuple([start_pos_tuple])}
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        # include_pos를 먼저 변환
        highlight_tiles = []
        # root_positions과 exclude_positions 설정
        root_positions = {(float(root[0].pos.x), float(root[0].pos.y)) for root in self.move_roots}
        exclude_positions = root_positions | {character_pos_tuple}
        if exclude_pos:
            exclude_positions |= {(float(pos.x), float(pos.y)) for pos in exclude_pos}
            
        # 각 위치에 배틀러가 있는지 미리 확인 (include_positions는 제외)
        battler_positions = {(float(battler.pos.x), float(battler.pos.y)) 
                            for battler in self.level.battler_sprites 
                            if battler != self.selected_battler and not battler.isdead}
        # include_pos에 있는 위치는 배틀러 위치에서만 제외
        target_pos = None
        if check_pos is not None:
            target_pos = (float(check_pos.x), float(check_pos.y))

        # include_pos를 튜플 세트로 변환
        # 각 위치에 배틀러가 있는지 미리 확인
        battler_positions = {(float(battler.pos.x), float(battler.pos.y)) 
                            for battler in self.level.battler_sprites 
                            if battler != self.selected_battler and not battler.isdead}
        # include_pos에 있는 위치는 배틀러 위치에서 제외
        while queue:
            # print(queue)
            current_pos, current_cost, current_path = queue.popleft()
            current_x, current_y = float(current_pos.x), float(current_pos.y)
            current_pos_tuple = (current_x, current_y)
            
            if target_pos and current_pos_tuple == target_pos:
                if current_pos_tuple not in paths:
                    paths[current_pos_tuple] = set()
                paths[current_pos_tuple].add(tuple(current_path))
            
            for dx, dy in directions:
                next_x = current_x + dx
                next_y = current_y + dy
                next_pos_tuple = (next_x, next_y)

                if (0 <= next_x < len(moves_data) and 
                    0 <= next_y < len(moves_data[0])):
                    
                    if moves_data[int(next_x)][int(next_y)] == '-1' or next_pos_tuple in exclude_positions:
                        continue

                    move_cost = int(moves_data[int(next_x)][int(next_y)])
                    total_cost = current_cost + move_cost
                    remaining_moves = moves_left - total_cost

                    # 배틀러가 있는 위치는 이동력 1 이상 필요 (include_pos는 제외)
                    if next_pos_tuple in battler_positions and remaining_moves < 1:
                        continue

                    if total_cost <= moves_left:
                        if next_pos_tuple not in visited or total_cost <= visited[next_pos_tuple]:
                            pixel_pos = (int(next_x * TILESIZE), int(next_y * TILESIZE))
                            
                            if remaining_moves >= 0:
                                if not (next_pos_tuple in battler_positions and remaining_moves < 1):
                                    new_path = current_path + [next_pos_tuple]
                                    
                                    if next_pos_tuple not in paths:
                                        paths[next_pos_tuple] = set()
                                    paths[next_pos_tuple].add(tuple(new_path))
                                    
                                    if next_pos_tuple not in visited or total_cost <= visited[next_pos_tuple]:
                                        queue.append((pygame.math.Vector2(next_x, next_y), total_cost, new_path))
                                    visited[next_pos_tuple] = total_cost

                                    if next_pos_tuple != character_pos_tuple:
                                        movable_positions.append((next_pos_tuple, remaining_moves))
                                        if not pygame.math.Vector2(next_x, next_y) in highlight_tiles:
                                            highlight_tiles.append(pygame.math.Vector2(next_x, next_y))
                                        
        if show:
            self.highlight_tiles_set(highlight_tiles,mode='Set',color='green')
        if target_pos and target_pos in paths:
            shortest_paths = [path for path in paths[target_pos] if len(path) > 1]
            if shortest_paths:
                total_cost = visited[target_pos]
                return shortest_paths
                
        return movable_positions

    def find_approach_path(self, start_pos, target_pos, moves, max_moves):
        """
        목표 지점이나 그 주변으로 가는 최적의 경로를 찾습니다.
        접근할 수 없는 경우 점점 더 넓은 범위에서 접근 가능한 위치를 찾습니다.
        """
        moves_data = self.level.level_data["moves"]
        paths_to_positions = {}  # {위치: [총비용, 경로]}
        
        target_tuple = (float(target_pos.x), float(target_pos.y))
        start_tuple = (float(start_pos.x), float(start_pos.y))
        
        # 맵 경계 확인
        map_width = len(moves_data[0])
        map_height = len(moves_data)
        
        # 다른 배틀러들의 위치
        battler_positions = {(float(battler.pos.x), float(battler.pos.y)) 
                            for battler in self.level.battler_sprites 
                            if battler != self.selected_battler and not battler.isdead}

        # Manhattan distance 기준으로 점점 넓혀가는 탐색
        max_search_distance = 5  # 최대 탐색 거리
        for distance in range(1, max_search_distance + 1):
            # 현재 거리에서의 모든 가능한 위치 생성
            target_area = []
            for dx in range(-distance, distance + 1):
                for dy in range(-distance, distance + 1):
                    if abs(dx) + abs(dy) == distance:  # Manhattan distance가 현재 거리와 같은 위치만
                        new_x = target_pos.x + dx
                        new_y = target_pos.y + dy
                        # 맵 범위 내에 있는지 확인
                        if 0 <= new_x < map_width and 0 <= new_y < map_height:
                            target_area.append((new_x, new_y))
            
            from heapq import heappush, heappop
            queue = [(0, start_tuple, [(start_tuple, 0)])]
            visited = set([start_tuple])
            
            while queue:
                current_cost, current_pos, current_path = heappop(queue)
                current_x, current_y = current_pos
                
                if current_cost > max_moves:
                    continue
                
                # 현재 탐색 거리의 위치에 도달했을 때
                if (current_x, current_y) in target_area:
                    if (current_x, current_y) not in paths_to_positions or paths_to_positions[(current_x, current_y)][0] > current_cost:
                        paths_to_positions[(current_x, current_y)] = [current_cost, current_path]
                    continue
                
                for dx, dy in [(0,1), (0,-1), (1,0), (-1,0)]:
                    next_x = current_x + dx
                    next_y = current_y + dy
                    next_pos = (next_x, next_y)
                    
                    if next_pos in visited:
                        continue
                    
                    if not (0 <= next_x < map_width and 0 <= next_y < map_height):
                        continue
                    
                    if moves_data[int(next_y)][int(next_x)] == '-1':
                        continue
                    
                    # 다른 배틀러가 있는 위치는 목표가 아니면 건너뛰기
                    if next_pos in battler_positions and next_pos != target_tuple:
                        continue

                    move_cost = 99 if moves_data[int(next_x)][int(next_y)].startswith('-') else int(moves_data[int(next_x)][int(next_y)])
                    new_cost = current_cost + move_cost
                    
                    if new_cost <= max_moves:
                        new_path = current_path + [(next_pos, new_cost)]
                        visited.add(next_pos)
                        heappush(queue, (new_cost, next_pos, new_path))
            
            # 현재 거리에서 도달 가능한 위치가 있으면 반환
            if paths_to_positions:
                # 찾은 위치들 중 목표와 가장 가까운 위치 선택
                best_pos = min(paths_to_positions.keys(),
                            key=lambda pos: (paths_to_positions[pos][0] + 
                                            ((pos[0]-target_tuple[0])**2 + 
                                            (pos[1]-target_tuple[1])**2)**0.5))
                return [paths_to_positions[best_pos]]
        
        return None

    def apply_skill_effects(self, target, skill_name, skill_level):
        """스킬 효과 적용"""
        skill_info = SKILL_PROPERTIES[skill_name]

        # 버프 스킬인 경우
        if skill_info['skill_type'] == 'buff':
            buff_duration = skill_info.get('duration', 1)
            # 퍼센트 효과 적용
            if 'Buff_%' in skill_info:
                effect = Effect(effect_type='buff',effects=skill_info['Buff_%'][skill_level],source=f"buff_{skill_name}",remaining_turns=buff_duration,is_percent=True)
                self.effect_manager.add_effect(target, effect)
            # 고정값 효과 적용
            if 'Buff' in skill_info:
                effect = Effect(effect_type='buff',effects=skill_info['Buff'][skill_level],source=f"buff_{skill_name}",remaining_turns=buff_duration)
                self.effect_manager.add_effect(target, effect)
            # 버프 시각 효과
            self.animation_manager.create_animation((target.collision_rect.centerx, target.collision_rect.centery),skill_info.get('animate', 'SHIELD'),wait=True)
            
        elif skill_info.get('Heal'):
            heal_amount = skill_info['Heal'][skill_level]+ self.selected_battler.stats["INT"]
            target.Cur_HP = min(target.stats["Max_HP"], target.Cur_HP + heal_amount )
            self.animation_manager.create_animation((target.collision_rect.centerx, target.collision_rect.top - 10),'DAMAGE',value=heal_amount)
        # 데미지 스킬인 경우
        else:
            target_magic_def = target.stats["INT"] * 0.2 + target.stats["RES"] * 0.4
            level_diff_bonus = (self.selected_battler.stats["INT"] - target.stats["INT"]) * 0.015
            skill_multiplier = skill_info.get('Dmg_Coff', {}).get(skill_level, 0)
            damage = ((1 + level_diff_bonus) * skill_multiplier * 1.5) - target_magic_def
            self.Acted.append([target,'Magic_Damage',damage])

            # 데미지 처리
            self.Damage(self.selected_battler, target, damage, "Magic")
            
            # 상태이상 적용
            if target.Cur_HP > 0 and 'Status_%' in skill_info:
                status_chances = skill_info['Status_%'].get(skill_level, {})
                for status, chance in status_chances.items():
                    if random.random() * 100 < chance:
                        effect = Effect(effect_type='status',effects=STATUS_PROPERTIES[status].get('Stat', {}),source=f"status_{status}",remaining_turns=STATUS_PROPERTIES[status]['duration'])
                        if 'Stat_%' in STATUS_PROPERTIES[status]:
                            effect_percent = Effect(effect_type='status',effects=STATUS_PROPERTIES[status]['Stat_%'],source=f"status_{status}_percent",remaining_turns=STATUS_PROPERTIES[status]['duration'],is_percent=True)
                            target.effects.append(effect_percent)
                        target.effects.append(effect)
                self.effect_manager.update_effects(target)

    def apply_support_skill_effects(self, source_battler, target_battler, skill_name, skill_level):
        """지원 스킬 효과 적용 (예: 전장의 함성)"""
        skill_info = SKILL_PROPERTIES[skill_name]
        
        if not skill_info.get('Support_type'):
            return
            
        # 회복 효과 처리
        if skill_info['Support_type'] == 'Recovery' and 'Support' in skill_info:
            support_values = skill_info['Support'][skill_level]
            for stat, value in support_values.items():
                if stat == 'Cur_HP':
                    heal_amount = value
                    target_battler.Cur_HP = min(target_battler.stats["Max_HP"], 
                                              target_battler.Cur_HP + heal_amount)
                    self.animation_manager.create_animation(
                        (target_battler.collision_rect.centerx, 
                         target_battler.collision_rect.top - 10),
                        'DAMAGE',
                        value=heal_amount
                    )

        # 소스 스탯 기반 버프
        elif skill_info['Support_type'] == 'Boost':
            if 'Support_%' in skill_info:
                buff_data = {'percent': {}}
                for stat, percent in skill_info['Support_%'][skill_level].items():
                    buff_value = int(source_battler.stats[stat] * (percent / 100))
                    buff_data['percent'][stat] = buff_value
                self.effect_manager.apply_temporary_buff(
                    target_battler,
                    f"support_{skill_name}",
                    buff_data,
                    duration=1  # 이동 페이즈 동안만 지속
                )

        # 기본 스탯 버프
        elif skill_info['Support_type'] == 'Boost_self':
            buff_data = {'percent': {}, 'flat': {}}
            
            if 'Support' in skill_info:
                for stat, value in skill_info['Support'][skill_level].items():
                    buff_data['flat'][stat] = value
                    
            if 'Support_%' in skill_info:
                for stat, percent in skill_info['Support_%'][skill_level].items():
                    buff_data['percent'][stat] = percent
                    
            if buff_data['percent'] or buff_data['flat']:
                self.effect_manager.apply_temporary_buff(
                    target_battler,
                    f"support_self_{skill_name}",
                    buff_data,
                    duration=1
                )

        if buff_data['percent'] or buff_data['flat']:
            # 버프 적용 시 시각 효과
            self.animation_manager.create_animation(target_battler, 'AURA', wait=True)
        
        self.map_action.effect_manager.update_effects(target_battler)

    def check_magic_range(self, battler, skill):
        skill_range = SKILL_PROPERTIES[skill].get('Range', {}).get(battler.skills[skill], 0)
        facing = self.temp_facing
        shape = SKILL_PROPERTIES[skill].get('shape', 'diamond')
        attackable_pos = []
        if shape == 'diamond':
            diamond = [(dx, dy) for dx in range(-skill_range, skill_range + 1) for dy in range(-skill_range, skill_range + 1) if abs(dx) + abs(dy) <= skill_range]    
            for dx, dy in diamond:
                attackable_pos.append([battler.pos.x + dx ,battler.pos.y  + dy ])
        elif shape == 'linear':
                # 방향별 오프셋 정의
            direction_offsets = {'up': (0, -1),'down': (0, 1),'left': (-1, 0),'right': (1, 0)}
            # 현재 방향 (또는 임시 방향) 기준으로 타일 생성
            facing = getattr(self, 'temp_facing', battler.facing)
            dx, dy = direction_offsets[facing]
            # 직선상의 타일 생성
            for i in range(1, skill_range + 1):
                attackable_pos.append([battler.pos.x + dx * i ,battler.pos.y  + dy * i])
        # print(attackable_pos)
        return attackable_pos

    def highlight_tiles_set(self,pos_list,mode = 'Set', color = 'yellow'):
        if mode == 'Set':
            for pos in pos_list:
                tile_image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
                pygame.draw.rect(tile_image, color, pygame.Rect(0, 0, TILESIZE, TILESIZE), 4)
                pygame.draw.rect(tile_image, 'black', pygame.Rect(0, 0, TILESIZE, TILESIZE), 1)
                tile_image.set_alpha(128)
                highlight_tile = Tile(pygame.math.Vector2(pos.x * TILESIZE, pos.y * TILESIZE),[self.visible_sprites],'area_display_tile')
                highlight_tile.image = tile_image
                highlight_tile.priority = highlight_tile.rect.topleft[1]
                self.highlight_tiles.append(highlight_tile)
                # tile = Tile((pos[0] * TILESIZE, pos[1] * TILESIZE), [self.level.visible_sprites], 'attackable_tile')
        elif mode == 'Clear':
            if self.highlight_tiles:
                # print(self.highlight_tiles)
                for tile in self.highlight_tiles:
                    tile.kill()
                self.highlight_tiles = []
        elif mode == 'Invisible':
            for tile in self.highlight_tiles:
                tile.image.set_alpha(0)

    def get_tiles_in_line(self, start_pos, end_pos, half_width=0.1):
        """
        두 위치 사이의 직선 경로에 있는 타일들을 반환
        start_pos: 시작 위치 (Vector2)
        end_pos: 끝 위치 (Vector2)
        half_width: 직선으로부터 타일을 체크할 거리
        """
        tiles = []
        checked = set()  # 이미 체크한 타일 위치를 저장
        
        # 두 점 사이의 거리와 방향 계산
        dx, dy = end_pos.x - start_pos.x, end_pos.y - start_pos.y
        distance = max(abs(dx), abs(dy))
        if distance == 0:
            return tiles
            
        # 각 단계별 증가량
        step_x, step_y = dx / distance, dy / distance
        
        # 직선을 따라 이동하면서 타일 체크
        for i in range(int(distance) + 1):
            # 현재 위치 계산
            current_x = (start_pos.x + 0.5) + step_x * i
            current_y = (start_pos.y + 0.5) + step_y * i

            # 주변 타일 체크 (직선으로부터 half_width 거리 이내의 타일)
            for ox in [-half_width, 0, half_width]:
                for oy in [-half_width, 0, half_width]:
                    check_x = int(current_x + ox)
                    check_y = int(current_y + oy)
                    
                    # 이미 체크한 타일이면 스킵
                    tile_pos = (check_x, check_y)
                    if tile_pos in checked:
                        continue
                    checked.add(tile_pos)

                    # 맵 범위 체크
                    if (0 <= check_x < len(self.level.level_data["moves"][0]) and 0 <= check_y < len(self.level.level_data["moves"][1])):
                        # moves 데이터로 타일 이동 가능 여부 체크
                        move_value = self.level.level_data["moves"][check_x][check_y]
                        tile_blocked = move_value == '-1'
                        
                        tiles.append({
                            'pos': pygame.math.Vector2(check_x, check_y),
                            'blocked': tile_blocked
                        })
                        
        return tiles

    def endturn(self):
        """턴 종료 시 처리"""
        self.target_battler = None
        self.interacted_battlers = []
        self.level.cursor.SW_select = False
        if self.selected_battler:
            # 캐릭터 상태 변경
            self.selected_battler.inactive = True
            self.selected_battler.isfollowing_root = False
            self.selected_battler.selected = False
            self.selected_battler.priority = self.selected_battler.pos.y * TILESIZE
            # print("@@삭제전 + "+str(self.selected_battler.stats))
            for effect in self.selected_battler.effects:
                if effect.type == 'supportbuff':
                    self.effect_manager.remove_effect(self.selected_battler, effect_type=effect.type)
            # print("@@삭제후 + "+str(self.selected_battler.stats))
            # 턴 행동에 따른 activate_condition 초기화
            if not all(battler.inactive for battler in self.level.battler_sprites if battler.team == self.current_phase and battler.pos != self.selected_battler.pos):
                # Check each action type using proper format
                for actions in self.Acted:
                    target = actions[0]
                    action = actions[1]
                    detail = actions[2] if len(actions) > 2 else None
                    # Movement action
                    if action == 'Move':
                        self.selected_battler.activate_condition['Turn_Without_Move'] = 0
                    
                    # Magic casting action
                    elif action == 'Magic_Casting':
                        self.selected_battler.activate_condition['Turn_Without_Magic'] = 0
                    # Skill casting action
                    elif action == 'Use_Skill':
                        self.selected_battler.activate_condition['Turn_Without_Skill'] = 0
                    
                    # Range attack action
                    elif action == 'Range':
                        self.selected_battler.activate_condition['Turn_Without_Range'] = 0
                    
                    # Melee attack action
                    elif action == 'Melee':
                        self.selected_battler.activate_condition['Turn_Without_Melee'] = 0

            self.selected_battler = None
        
        if all(battler.inactive for battler in self.level.battler_sprites 
            if battler.team == self.current_phase):
            self.change_state('phase_change')
        else:
            self.level.cursor.select_lock = False
            self.level.cursor.move_lock = False
            self.change_state('explore')

        print(self.Acted)        

        self.Acted = []   
    
    def Damage(self, attacker, target, damage, damage_type, is_critical=False):
        """데미지 처리 및 관련 효과 적용"""
        # 현재 사용 중인 스킬의 스타일 확인
        is_healing = False
        if damage_type == "Magic" and hasattr(self, 'skill'):
            skill_info = SKILL_PROPERTIES[self.skill]
            is_healing = skill_info.get('style') == 'support'
        
        if not is_healing:
            # 데미지의 경우 음수가 되지 않도록 (회복 방지)
            damage = max(0, damage)

        # 애니메이션 생성 (회복은 양수로, 데미지는 음수로 표시)
        display_value = -damage
        
        if is_critical:
            self.animation_manager.create_animation(
                (target.collision_rect.centerx, target.collision_rect.top - 10),
                'CRITICAL_DAMAGE',
                value=display_value
            )
        else:
            self.animation_manager.create_animation(
                (target.collision_rect.centerx, target.collision_rect.top - 10),
                'DAMAGE',
                value=display_value
            )

        # 경험치 계산을 위한 데이터
        kill_exp = CharacterDatabase.data[target.char_type].get('Kill_EXP', 0)
        max_hp = target.stats["Max_HP"]
        cha_multiplier = attacker.stats["CHA_increase_multiplier"]
        dmg_ratio = abs(damage) / max_hp
        
        # 데미지/회복 적용
        if is_healing:
            target.Cur_HP = min(target.Cur_HP - damage, target.stats["Max_HP"])
            attacker.tmp_exp_gain += kill_exp * dmg_ratio * 0.5  # 회복은 절반의 경험치
        else:
            if damage > target.Cur_HP:
                target.Cur_HP = 0
                attacker.tmp_exp_gain += kill_exp * (1 + target.Cur_HP / max_hp)
                
                # CHA 증가 효과
                cha_boost = int(5 * cha_multiplier * (1 + dmg_ratio))
                self.effect_manager.apply_temporary_buff(attacker,'cha_boost',{'flat': {'CHA': cha_boost}},duration=None)
            else:
                target.Cur_HP -= damage
                attacker.tmp_exp_gain += kill_exp * dmg_ratio
                
                # CHA 증가 효과
                cha_boost = int(5 * cha_multiplier * dmg_ratio)
                self.effect_manager.apply_temporary_buff(attacker,'cha_boost',{'flat': {'CHA': cha_boost}},duration=None)

        # 상태이상이나 조건부 효과들 체크
        self.effect_manager.update_effects(target)  # 대상의 효과 업데이트
        self.effect_manager.update_effects(attacker)  # 공격자의 효과 업데이트
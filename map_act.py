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
        self.animate_pos = None
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
                exp_gain = battler.tmp_exp_gain * (1 + 0.01 * battler.stats["CHA"]) * battler.stats["EXP_mul"]
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
                    self.animation_manager.create_animation((battler.collision_rect.centerx, battler.collision_rect.top - 10),'DAMAGE',value=heal_amount)
                elif stat == 'Cur_MP':
                    heal_amount = int(battler.stats['Max_MP'] * value / 100)
                    battler.Cur_MP = min(battler.stats['Max_MP'], battler.Cur_MP + heal_amount)
                    
        # 고정값 힐링
        elif 'Heal' in effect_data:
            for stat, value in effect_data['Heal'].items():
                if stat == 'Cur_HP':
                    battler.Cur_HP = min(battler.stats['Max_HP'], battler.Cur_HP + value)
                    self.animation_manager.create_animation((battler.collision_rect.centerx, battler.collision_rect.top - 10),'DAMAGE',value=value)
                elif stat == 'Cur_MP':
                    battler.Cur_MP = min(battler.stats['Max_MP'], battler.Cur_MP + value)
        
        # 버프 효과 적용
        duration = effect_data.get('duration', None)
        
        # 퍼센트 효과가 있다면
        if 'Buff_%' in effect_data:
            effect = Effect(effect_type='item_buff',effects=effect_data['Buff_%'],source=f"item_{item_name}_percent",remaining_turns=duration,is_percent=True)
            self.effect_manager.add_effect(battler, effect)
        
        # 고정값 효과가 있다면
        if 'Buff' in effect_data:
            effect = Effect(effect_type='item_buff',effects=effect_data['Buff'],source=f"item_{item_name}",remaining_turns=duration)
            self.effect_manager.add_effect(battler, effect)
        
       # 영구 Change 효과가 있다면
        if 'Change' in effect_data:
            effect = Effect(effect_type='change',effects=effect_data['Change'],source=f"change_{item_name}",remaining_turns=None)  # 영구 지속
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
        skill_info = SKILL_PROPERTIES[skill_name]['Active']

        # 버프 스킬인 경우
        if skill_info['skill_type'] == 'buff':
            buff_duration = skill_info['effects'].get('duration', 1)
            # 퍼센트 효과 적용
            if skill_info['effects'].get('stats_%',{}):
                effect = Effect(effect_type='buff',effects=skill_info['effects']['stats_%'][skill_level],source=f"buff_{skill_name}",remaining_turns=buff_duration,is_percent=True)
                self.effect_manager.add_effect(target, effect)
            # 고정값 효과 적용
            if skill_info['effects'].get('stats',{}):
                effect = Effect(effect_type='buff',effects=skill_info['effects']['stats'][skill_level],source=f"buff_{skill_name}",remaining_turns=buff_duration)
                self.effect_manager.add_effect(target, effect)
            # 버프 시각 효과
            self.animation_manager.create_animation((target.collision_rect.centerx, target.collision_rect.centery),skill_info.get('animate', 'SHIELD'),wait=True)
            
        # 짧은 버프 스킬인 경우
        if skill_info['skill_type'] == 'buff_temp':
            buff_duration = None
            # 퍼센트 효과 적용
            if skill_info['effects'].get('stats_%',{}):
                effect = Effect(effect_type='buff_until_turn',effects=skill_info['effects']['stats_%'][skill_level],source=f"buff_temp_{skill_name}",remaining_turns=buff_duration,is_percent=True)
                self.effect_manager.add_effect(target, effect)
            # 고정값 효과 적용
            if skill_info['effects'].get('stats',{}):
                effect = Effect(effect_type='buff_until_turn',effects=skill_info['effects']['stats'][skill_level],source=f"buff_temp_{skill_name}",remaining_turns=buff_duration)
                self.effect_manager.add_effect(target, effect)
            # 버프 시각 효과
            self.animation_manager.create_animation((target.collision_rect.centerx, target.collision_rect.centery),skill_info.get('animate', 'SHIELD'),wait=True)
            
        elif skill_info['skill_type'] == 'heal':
            heal_amount = skill_info['damage']['dmg_coef'][skill_level] + self.selected_battler.stats["INT"]
            target.Cur_HP = min(target.stats["Max_HP"], target.Cur_HP + heal_amount )
            self.animation_manager.create_animation((target.collision_rect.centerx, target.collision_rect.top - 10),'DAMAGE',value=heal_amount)
        # 데미지 스킬인 경우
        else:
            if skill_info['damage']['dmg_type'] == 'magical':
                target_magic_def = target.stats["INT"] * 0.2 + target.stats["RES"] * 0.4
                level_diff_bonus = (self.selected_battler.stats["INT"] - target.stats["INT"]) * 0.015
                skill_multiplier = skill_info['damage'].get('dmg_coef', {}).get(skill_level, 0)
                damage = ((1 + level_diff_bonus) * skill_multiplier * 1.5) - target_magic_def
                self.Acted.append([target,'Magic_Damage',damage])

                # 데미지 처리
                self.Damage(self.selected_battler, target, damage, "Magic")
                
                # 상태이상 적용
                if target.Cur_HP > 0 and skill_info['effects'].get(skill_level, None):
                    status_chances = skill_info['status'].get(skill_level, {})
                    for status, chance in status_chances.items():
                        if random.random() * 100 < chance:
                            effect = Effect(effect_type='status',effects=STATUS_PROPERTIES[status].get('Stat', {}),source=f"status_{status}",remaining_turns=STATUS_PROPERTIES[status]['duration'])
                            if 'Stat_%' in STATUS_PROPERTIES[status]:
                                effect_percent = Effect(effect_type='status',effects=STATUS_PROPERTIES[status]['Stat_%'],source=f"status_{status}_percent",remaining_turns=STATUS_PROPERTIES[status]['duration'],is_percent=True)
                                target.effects.append(effect_percent)
                            target.effects.append(effect)
                    self.effect_manager.update_effects(target)

    def check_magic_range(self, battler, skill):
        skill_range = SKILL_PROPERTIES[skill]['Active'].get('range',{}).get(battler.skills[skill], 0)
        
        facing = self.temp_facing
        shape = SKILL_PROPERTIES[skill]['Active'].get('range_type',None)
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
        elif shape == 'cross':
            cross = [(dx, dy) for dx in range(-skill_range, skill_range + 1) for dy in range(-skill_range, skill_range + 1) if dx == 0 or dy == 0]
            for dx, dy in cross:
                attackable_pos.append([battler.pos.x + dx ,battler.pos.y  + dy ])
        elif shape == 'square':
            square = [(dx, dy) for dx in range(-skill_range, skill_range + 1) for dy in range(-skill_range, skill_range + 1)]
            for dx, dy in square:
                attackable_pos.append([battler.pos.x + dx ,battler.pos.y  + dy ])
        
        return attackable_pos

    def check_magic_area(self,battler,skill,cursor):
        skill_info = SKILL_PROPERTIES[skill]['Active']
        area_range = skill_info['area']['range'].get(battler.skills[skill],0)
        attackable_area = []
        if skill_info['area']['type'] == 'diamond':
            diamond = [(dx, dy) for dx in range(-area_range, area_range + 1) for dy in range(-area_range, area_range + 1) if abs(dx) + abs(dy) <= area_range]
            for dx, dy in diamond:
                attackable_area.append([cursor.pos.x + dx ,cursor.pos.y  + dy ])
        return attackable_area

    def highlight_tiles_set(self,pos_list,mode = 'Set', color = 'yellow',identifier = ''):
        if mode == 'Set':
            for pos in pos_list:
                tile_image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
                pygame.draw.rect(tile_image, color, pygame.Rect(0, 0, TILESIZE, TILESIZE), 4)
                pygame.draw.rect(tile_image, 'black', pygame.Rect(0, 0, TILESIZE, TILESIZE), 1)
                tile_image.set_alpha(128)
                highlight_tile = Tile(pygame.math.Vector2(pos.x * TILESIZE, pos.y * TILESIZE),[self.visible_sprites],'area_display_tile')
                highlight_tile.image = tile_image
                highlight_tile.identifier = identifier
                if identifier == 'area':
                    highlight_tile.priority = highlight_tile.rect.topleft[1] + 1
                else:
                    highlight_tile.priority = highlight_tile.rect.topleft[1]
                self.highlight_tiles.append(highlight_tile)
                # tile = Tile((pos[0] * TILESIZE, pos[1] * TILESIZE), [self.level.visible_sprites], 'attackable_tile')
        elif mode == 'Clear':
            if self.highlight_tiles:
                tiles_to_remove = [tile for tile in self.highlight_tiles if tile.identifier == identifier]
                for tile in tiles_to_remove:
                    tile.kill()
                    self.highlight_tiles.remove(tile)
        elif mode == 'All_Clear':
            for tile in self.highlight_tiles:
                tile.kill()
            self.highlight_tiles = []
        elif mode == 'Invisible':
            for tile in self.highlight_tiles:
                tile.image.set_alpha(0)

    def get_tiles_in_line(self, start_pos, end_pos):
        """
        두 위치 사이의 직선이 지나는 타일들을 순서대로 찾고,
        각 타일에서 다음 타일로의 이동이 가능한지 체크
        start_pos: 시작 위치 (Vector2)
        end_pos: 끝 위치 (Vector2)
        """
        tiles = []
        
        # 시작점과 끝점의 정수 좌표
        x1, y1 = int(start_pos.x), int(start_pos.y)
        x2, y2 = int(end_pos.x), int(end_pos.y)
        
        # 브레젠험 알고리즘으로 선이 지나는 타일들 찾기
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        sx = 1 if x2 > x1 else -1
        sy = 1 if y2 > y1 else -1
        err = dx - dy
        
        x, y = x1, y1
        path_tiles = []
        
        while True:
            path_tiles.append((x, y))
            if x == x2 and y == y2:
                break
                
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy
        
        # 각 타일에서 다음 타일로의 이동이 가능한지 체크
        for i in range(len(path_tiles) - 1):
            current_x, current_y = path_tiles[i]
            next_x, next_y = path_tiles[i + 1]
            
            # 맵 범위 체크
            if (0 <= current_x < len(self.level.level_data["ranges"][0]) and 
                0 <= current_y < len(self.level.level_data["ranges"])):
                
                # 다음 타일과의 방향 차이로 이동 방향 결정
                dx = next_x - current_x
                dy = next_y - current_y
                
                # 8방향 이동 판정
                # 0: 상단, 1: 우상단, 2: 우단, 3: 우하단, 4: 하단, 5: 좌하단, 6: 좌단, 7: 좌상단
                direction = -1
                if dx == 0 and dy == -1: direction = 0      # 상
                elif dx == 1 and dy == -1: direction = 1    # 우상
                elif dx == 1 and dy == 0: direction = 2     # 우
                elif dx == 1 and dy == 1: direction = 3     # 우하
                elif dx == 0 and dy == 1: direction = 4     # 하
                elif dx == -1 and dy == 1: direction = 5    # 좌하
                elif dx == -1 and dy == 0: direction = 6    # 좌
                elif dx == -1 and dy == -1: direction = 7   # 좌상
                
                # 현재 타일의 range_data 확인
                range_value = self.level.level_data["ranges"][current_x][current_y]
                is_blocked = False
                
                # range_data가 리스트인 경우 (방향별 제한이 있는 경우)
                if isinstance(range_value, list):
                    is_blocked = str(direction) in range_value
                # 완전 차단된 경우
                elif range_value == '40':
                    is_blocked = True
                    
                tiles.append({
                    'pos': pygame.math.Vector2(current_x, current_y),
                    'blocked': is_blocked
                })
                
                # 현재 타일이 막혀있으면 더 이상 진행하지 않음
                if is_blocked:
                    break
        # 마지막 타일 추가
        if path_tiles:
            last_x, last_y = path_tiles[-1]
            if (0 <= last_x < len(self.level.level_data["ranges"][0]) and 
                0 <= last_y < len(self.level.level_data["ranges"])):
                range_value = self.level.level_data["ranges"][last_y][last_x]
                is_blocked = range_value == '40'
                tiles.append({
                    'pos': pygame.math.Vector2(last_x, last_y),
                    'blocked': is_blocked
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
        cha_multiplier = attacker.stats["CHA_increase_mul"]
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
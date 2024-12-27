# map_act.py
import pygame
from properties import *
from tile import Tile
from database import *
from collections import deque
import random
from support import SoundManager, InputManager
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
        self.AI = AI(self)
        self.update_time = 0
        self.step_enemy_turns = False
        self.movable_tiles = []
        self.highlight_tiles = []
        self.current_skill_index = 0  # 선택된 스킬 인덱스 추가
        self.current_Class = ''
        self.battle_exp_gain = 0
        self.current_dialog = None
        self.path_dragging = False
        self.last_drag_pos = None
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

 ##### 캐릭터 스탯, 버프 처리
    def apply_status(self, battler, status_name, duration):
        """상태이상 적용"""
        battler.state = status_name
        battler.status_duration = duration
        self.recalculate_stats(battler)

    def update_status(self, battler):
        """상태이상 업데이트"""
        if battler.state and battler.status_duration > 0:
            old_state = battler.state
            battler.status_duration -= 1
            if battler.status_duration <= 0:
                battler.state = None
                self.recalculate_stats(battler, update_only=True)  # 턴 감소/제거 시에는 update_only=True

    def apply_buff(self, battler, buff_name, stat_changes, turns=None):
        """
        버프/디버프 적용
        stat_changes는 퍼센트와 고정값 변화를 구분하여 저장
        """
        # 기존의 같은 이름 버프 제거
        battler.buffs = [buff for buff in battler.buffs if buff['name'] != buff_name]
        
        # 새 버프 형식으로 변환
        if isinstance(stat_changes, dict) and 'percent' in stat_changes and 'flat' in stat_changes:
            # 이미 적절한 형식으로 전달된 경우
            formatted_stats = stat_changes
        else:
            # 구 형식 변환 작업
            formatted_stats = {
                'percent': {},
                'flat': {}
            }
            
            if isinstance(stat_changes, dict):
                has_percent = False
                # Buff_%나 Status_%로 전달된 경우를 처리
                for key, value in stat_changes.items():
                    if isinstance(value, dict):  # 내부가 딕셔너리인 경우
                        if key == 'percent':
                            formatted_stats['percent'].update(value)
                            has_percent = True
                        elif key == 'flat':
                            formatted_stats['flat'].update(value)
                        else:
                            # 일반 스탯인 경우 flat으로 처리
                            formatted_stats['flat'][key] = value
                    else:
                        # 직접 값이 전달된 경우 flat으로 처리
                        formatted_stats['flat'][key] = value
        
        # 새 버프 추가
        battler.buffs.append({
            'name': buff_name,
            'stats': formatted_stats,
            'turns': turns
        })
        
        self.recalculate_stats(battler)

    def recalculate_stats(self, battler, update_only=False):
        """모든 스탯 재계산"""
        # 1. 기본 스탯으로 초기화
        old_stats = battler.stats.copy() if hasattr(battler, 'stats') else {}
        battler.stats = battler.base_stats.copy()
        
        battler.stats['CHA'] += battler.combat_cha_boost
        # 2. 장비 효과 적용
        equipment_mods = {
            'percent': {},  # multiplier 계열
            'flat': {}     # 일반 스탯
        }
        
        for equip_name in battler.equips:
            if equip_name not in EQUIP_PROPERTIES:
                continue
                
            equip_stats = EQUIP_PROPERTIES[equip_name]['STAT']
            for stat, value in equip_stats.items():
                if 'multiplier' in stat.lower():
                    # multiplier 계열은 퍼센트 수정치로 처리
                    equipment_mods['percent'][stat] = equipment_mods['percent'].get(stat, 0) + value
                else:
                    # 일반 스탯은 고정값으로 처리
                    equipment_mods['flat'][stat] = equipment_mods['flat'].get(stat, 0) + value

        # 3. 퍼센트 수정치 계산 (장비 + 상태이상 + 버프)
        percent_mods = equipment_mods['percent'].copy()
        
        # 3.1 상태이상으로 인한 퍼센트 수정치
        if battler.state and battler.state in STATUS_PROPERTIES:
            status_percent = STATUS_PROPERTIES[battler.state].get('Stat_%', {})
            for stat, mod in status_percent.items():
                if stat in battler.stats:
                    percent_mods[stat] = percent_mods.get(stat, 0) + mod

        # 3.2 버프/디버프로 인한 퍼센트 수정치
        for buff in battler.buffs:
            if 'stats' in buff and buff['stats'].get('percent'):
                for stat, mod in buff['stats']['percent'].items():
                    if stat in battler.stats:
                        percent_mods[stat] = percent_mods.get(stat, 0) + mod

        # 퍼센트 수정치 적용
        for stat, total_percent in percent_mods.items():
            if stat in battler.stats:
                battler.stats[stat] = battler.stats[stat] * (1 + total_percent/100)

        # 4. 고정값 수정치 적용 (장비 + 상태이상 + 버프)
        flat_mods = equipment_mods['flat'].copy()
        
        # 4.1 상태이상으로 인한 고정값 수정치
        if battler.state and battler.state in STATUS_PROPERTIES:
            status_flat = STATUS_PROPERTIES[battler.state].get('Stat', {})
            for stat, mod in status_flat.items():
                if stat in battler.stats:
                    flat_mods[stat] = flat_mods.get(stat, 0) + mod

        # 4.2 버프/디버프로 인한 고정값 수정치
        for buff in battler.buffs:
            if 'stats' in buff and buff['stats'].get('flat'):
                for stat, mod in buff['stats']['flat'].items():
                    if stat in battler.stats:
                        flat_mods[stat] = flat_mods.get(stat, 0) + mod

        # 고정값 수정치 적용
        for stat, mod in flat_mods.items():
            if stat in battler.stats:
                battler.stats[stat] += mod

        # 4. multiplier 관련 스탯은 최소값 0.2로 보정
        for stat in battler.stats:
            if 'multiplier' in stat.lower():
                battler.stats[stat] = max(0.2, battler.stats[stat])
        
        # 5. 정수로 처리할 스탯들 처리
        integer_stats = ['Max_HP', 'Max_MP', 'STR', 'DEX', 'INT', 'RES', 'Mov', 'CHA']
        for stat in integer_stats:
            if stat in battler.stats:
                battler.stats[stat] = int(battler.stats[stat])

        # 상태이상 효과 적용
        if battler.state and battler.state in STATUS_PROPERTIES:
            effects = STATUS_PROPERTIES[battler.state].get('Effects', [])
            battler.force_inactive = 'inactive' in effects
        
        # 스탯 변화 애니메이션 처리 (업데이트 중에는 생략)
        if self.animation_manager and old_stats and not update_only and self.current_mode != 'init':
            stat_changes = []
            offset = 0
            main_stats = ['STR', 'DEX', 'INT', 'RES']
            
            for stat in main_stats:
                if stat in battler.stats and stat in old_stats and battler.stats[stat] != old_stats[stat]:
                    stat_changes.append((stat, battler.stats[stat] > old_stats[stat], offset))
                    offset -= 24
            
            if battler.state:
                stat_changes.append((STATUS_PROPERTIES[battler.state].get('Notification', battler.state), None, offset))
                offset -= 24

            if stat_changes:
                for stat_info in stat_changes:
                    self.animation_manager.create_animation(battler,'STAT_CHANGE',value=stat_info,)

    def update_buffs(self, battler):
        """버프 상태 업데이트"""
        # 만료된 버프 제거 및 효과 제거
        remaining_buffs = []
        buffs_changed = False
        
        for buff in battler.buffs:
            # 영구 지속 버프는 건너뛰기
            if buff['turns'] is None:
                remaining_buffs.append(buff)
                continue
            
            buff['turns'] -= 1
            if buff['turns'] > 0:
                remaining_buffs.append(buff)
            else:
                buffs_changed = True
        
        battler.buffs = remaining_buffs
        # 버프가 제거된 경우에만 스탯 재계산
        if buffs_changed:
            self.recalculate_stats(battler, update_only=True)  # 턴 감소/제거 시에는 update_only=True

    def apply_passive_skills(self, battler):
        """패시브 스킬 효과 적용"""
        for skill_name, skill_level in battler.skills.items():
            skill_info = SKILL_PROPERTIES.get(skill_name)
            if skill_info and skill_info['Type'] == 'Passive':
                # 모든 수정치를 buff_data로 통합
                buff_data = {
                    'percent': skill_info.get('Buff_%', {}).get(skill_level, {}),
                    'flat': skill_info.get('Buff', {}).get(skill_level, {})
                }
                self.apply_buff(battler, f"{skill_name}_passive", buff_data, turns=None)
##### 경험치 습득 및 레벨업 처리
    def process_exp_gain(self):
        """경험치 획득과 레벨업 처리"""
        # 경험치 획득량 계산
        for battler in self.level.battler_sprites:
            if battler.tmp_exp_gain:
                # print(battler.tmp_exp_gain)
                battler.exp += battler.tmp_exp_gain * (1 + 0.01 * battler.stats["CHA"]) * battler.stats["EXP_multiplier"]
                battler.tmp_exp_gain = 0
                # 레벨업 했는 지 확인
                while battler.exp >= battler.stats['Max_EXP']:
                    # 초과 경험치 계산
                    excess_exp = battler.exp - battler.stats['Max_EXP']
                    
                    # 레벨업
                    battler.LV += 1
                    
                    # 새로운 스탯 계산
                    new_stats = CharacterDatabase.calculate_stats(battler.char_type, battler.LV)
                    
                    battler.Cur_HP = min(battler.Cur_HP + new_stats["Max_HP"] - battler.stats['Max_HP'] + battler.stats["Level_Up_Regen"] * new_stats["Max_HP"], new_stats["Max_HP"])
                    battler.Cur_MP = min(battler.Cur_MP + new_stats["Max_MP"] - battler.stats['Max_MP'] + battler.stats["Level_Up_Regen"] * new_stats["Max_MP"], new_stats["Max_MP"])
                    battler.base_stats = new_stats.copy()
                    self.recalculate_stats(battler, update_only=True)
                    # HP와 MP를 최대치로 회복
                    
                    # 초과 경험치 이전
                    battler.exp = excess_exp
                    
                    # 레벨업 애니메이션 생성
                    self.animation_manager.create_animation(battler, 'LEVEL_UP')
                    self.animation_manager.create_animation(battler, 'AURA')
       
    def use_item(self, battler, item_name):
        """아이템 사용 처리"""
        if item_name not in self.selected_battler.inventory:
            return False
            
        item_data = ITEM_PROPERTIES[item_name]
        effect = item_data['Effect']
        
        # 힐링 처리
        if 'Heal_%' in effect:
            for stat, value in effect['Heal_%'].items():
                if stat == 'Cur_HP':
                    heal_amount = int(battler.stats['Max_HP'] * value / 100)
                    print(heal_amount)
                    battler.Cur_HP = min(battler.stats['Max_HP'], battler.Cur_HP + heal_amount)
                    # 힐링 수치 표시 애니메이션 추가
                    self.animation_manager.create_animation((battler.collision_rect.centerx, battler.collision_rect.top - 10),'DAMAGE',value=heal_amount)
                elif stat == 'Cur_MP':
                    heal_amount = int(battler.stats['Max_MP'] * value / 100)
                    battler.Cur_MP = min(battler.stats['Max_MP'], battler.Cur_MP + heal_amount)
                    
        elif 'Heal' in effect:
            for stat, value in effect['Heal'].items():
                if stat == 'Cur_HP':
                    battler.Cur_HP = min(battler.stats['Max_HP'], battler.Cur_HP + value)
                    # 힐링 수치 표시 애니메이션 추가
                    self.animation_manager.create_animation((battler.collision_rect.centerx, battler.collision_rect.top - 10),'DAMAGE',value=value)
                elif stat == 'Cur_MP':
                    battler.Cur_MP = min(battler.stats['Max_MP'], battler.Cur_MP + value)
        
        elif 'Change' in effect:
            for stat,value in effect['Change'].items():
                if stat == 'CHA':
                    battler.stats["CHA"] = battler.stats["CHA"] + value
        # 버프 처리
        if 'Buff' in effect or 'Buff_%' in effect:
            duration = effect.get('duration', None)  # None이면 영구 지속
            buff_data = {
                'percent': effect.get('Buff_%', {}),
                'flat': effect.get('Buff', {})
            }
            self.apply_buff(battler,f"{item_name}_effect", buff_data, duration)
        
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

                if (0 <= next_x < len(moves_data[0]) and 
                    0 <= next_y < len(moves_data)):
                    
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

    def apply_skill_effects(self, target):
        """스킬 효과(데미지/상태이상 등) 적용"""
        skill_info = SKILL_PROPERTIES[self.skill]
        skill_level = self.selected_battler.skills[self.skill]
        
        # 데미지 계산 및 적용
        target_magic_def = target.stats["INT"] * 1.2 + target.stats["RES"] * 0.4
        level_diff_bonus = (self.selected_battler.stats["INT"] - target.stats["INT"]) * 0.015
        skill_multiplier = skill_info.get('Dmg_Coff', {}).get(skill_level, 0)
        Damage = ((1 + level_diff_bonus) * skill_multiplier * 1.5) - target_magic_def
        
        self.Damage(self.selected_battler,target,Damage,type='Magic')


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
        self.target_battler = None
            
        self.interacted_battlers = []
        self.level.cursor.SW_select = False
        if (self.current_Class == 'Magic' or 'Range') and not all(battler.inactive for battler in self.level.battler_sprites if battler.team == self.current_phase and battler.pos != self.selected_battler.pos):
            # print("되돌아감")
            self.visible_sprites.focus_on_target(self.selected_battler, self.level.cursor)
            self.level.cursor.rect.center = self.selected_battler.collision_rect.center
        self.current_Class = ''
        if self.selected_battler:
        # 임시 버프 제거
            if any(buff for buff in self.selected_battler.buffs if (buff['name'].startswith('temp_'))):
                self.selected_battler.buffs = [buff for buff in self.selected_battler.buffs if not (buff['name'].startswith('temp_') or buff['name'].endswith('_temp'))]
            # 버프 제거 후 스탯 재계산
                self.recalculate_stats(self.selected_battler)
            # 배틀러 상태 변경
            self.selected_battler.inactive = True   # 이동 종료 후 해당 캐릭터 비활성화
            self.selected_battler.isfollowing_root = False
            self.selected_battler.selected = False
            self.selected_battler.priority = self.selected_battler.pos.y * TILESIZE
            self.selected_battler = None
        if all(battler.inactive for battler in self.level.battler_sprites if battler.team == self.current_phase):
            self.change_state('phase_change')
        else:
            self.level.cursor.select_lock = False
            self.level.cursor.move_lock = False
            self.change_state('explore')

    def Damage(self,selected_battler,target_battler,Damage,type):
        self.animation_manager.create_animation((target_battler.collision_rect.centerx, target_battler.collision_rect.top - 10),'DAMAGE', value=-Damage)
        if type in ("Melee", "Range", "Magic"):
            kill_exp = CharacterDatabase.data[target_battler.char_type].get('Kill_EXP', 0)
            max_hp = target_battler.stats["Max_HP"]
            cha_multiplier = selected_battler.stats["CHA_increase_multiplier"]
            dmg_ratio = Damage / max_hp

            if Damage > target_battler.Cur_HP:
                # 적을 쓰러뜨린 경우
                target_battler.Cur_HP = 0
                selected_battler.tmp_exp_gain += kill_exp * (1 + target_battler.Cur_HP / max_hp)
                selected_battler.combat_cha_boost += int(5 * cha_multiplier * (1 + dmg_ratio))
                self.recalculate_stats(selected_battler)
            else:
                # 적을 쓰러뜨리지 못한 경우
                target_battler.Cur_HP -= Damage
                selected_battler.tmp_exp_gain += kill_exp * dmg_ratio
                selected_battler.combat_cha_boost += int(5 * cha_multiplier * (dmg_ratio))
                self.recalculate_stats(selected_battler)

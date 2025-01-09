# ai.py
from database import CharacterDatabase, SKILL_PROPERTIES
import pygame
from tile import Tile
from properties import *
import random
from common_method import istarget
class AI():
    def __init__(self,map_action):
        self.map_action = map_action
        self.level = map_action.level        
        self.current_phase = map_action.current_phase
        self.cur_moves = None
        self.result_temp_move_roots = []
        
    def battler_init(self):
        self.selected_battler = self.map_action.selected_battler
        self.max_moves = self.selected_battler.stats["Mov"]
        self.char_type = self.selected_battler.char_type
        self.char_data = CharacterDatabase.data.get(self.char_type, {})
        self.Class = self.char_data
        self.battlersEnemies = [battler for battler in self.level.battler_sprites if battler.team != self.selected_battler.team]
        self.result_temp_move_roots = []
        self.afterattack_move_type = '후퇴'
        
    def melee_ai(self):
        temp_move_roots = []
        
        start_pos = self.selected_battler.pos
        cur_moves = self.max_moves
        battler = None
        excluded_targets = set()  # 공격 불가능한 타겟들을 저장할 집합

        while cur_moves > 0:
            excluded_list = temp_move_roots[:] + [self.selected_battler.pos]
            movable_tiles = self.map_action.check_movable_from_pos(start_pos, cur_moves, exclude_pos=excluded_list, show=False)
            searched = []
            movable_positions = {pos for pos, moves in movable_tiles}
            sorted_battlers = sorted([b for b in self.battlersEnemies if b not in excluded_targets],key=lambda x: x.stats["CHA"],reverse=True)
            for searching_battler in sorted_battlers:
                # 현재 찾은 최대 CHA보다 작으면 더 이상 검색할 필요 없음
                if searched and searching_battler.stats["CHA"] <= searched[0].stats["CHA"]:
                    break
                    
                # 배틀러 위치가 이동 가능한 타일인지 확인
                battler_pos = (float(searching_battler.pos.x), float(searching_battler.pos.y))
                if battler_pos in movable_positions:
                    # 해당 타일의 remaining_moves 찾기
                    for tile_pos, remaining_moves in movable_tiles:
                        if tile_pos == battler_pos:
                            # 공격 후 후퇴 가능한지 확인
                            target_movable_tiles = self.map_action.check_movable_from_pos(searching_battler.pos, remaining_moves, show=False,exclude_pos=excluded_list)
                            # 후퇴할 공간이 없으면 이 대상은 제외
                            if not target_movable_tiles:
                                excluded_targets.add(searching_battler)
                                continue
                            
                            searched = [searching_battler, battler_pos, remaining_moves]
                            break

            if searched:
                battler, tile_pos, remaining_moves = searched
                
                paths = self.map_action.check_movable_from_pos(start_pos, cur_moves, check_pos=pygame.math.Vector2(tile_pos), exclude_pos=excluded_list)
                
                random_path = random.choice(paths)
                vector_list = [pygame.math.Vector2(t) for t in random_path]
                
                temp_move_roots.extend(vector_list[1:])
                start_pos = battler.pos
                cur_moves = remaining_moves
            else:
                if temp_move_roots and cur_moves and battler:
                    target_battler_movable_tiles = self.map_action.check_movable_from_pos(battler.pos, battler.stats['Mov'], show=False,except_self= True)
                    
                    if not target_battler_movable_tiles:
                        # 현재 타겟을 제외 목록에 추가하고 처음부터 다시 시작
                        print(f"{battler.name} 후퇴 공간 없음 - 다른 타겟 검색")
                        excluded_targets.add(battler)
                        start_pos = self.selected_battler.pos
                        cur_moves = self.max_moves
                        temp_move_roots = []
                        battler = None
                        continue
                    
                    safe_tile = self.delete_movable_tiles(movable_tiles, target_battler_movable_tiles)
                    zero_moves_tiles = [pos for pos, moves in movable_tiles if moves == 0]
                    if safe_tile:
                        after_attack_tile = min(safe_tile, key=lambda item: self.selected_battler.pos.distance_to(pygame.math.Vector2(item)))
                    elif zero_moves_tiles:  
                        after_attack_tile = min(zero_moves_tiles, key=lambda item: self.selected_battler.pos.distance_to(pygame.math.Vector2(item)))
                    elif movable_tiles:
                        other_battler_positions = {(battler.pos.x, battler.pos.y) for battler in self.level.battler_sprites if battler != self.selected_battler}
                        non_overlapping_zero_tiles = [pos for pos in zero_moves_tiles if (pos[0], pos[1]) not in other_battler_positions]
                        if non_overlapping_zero_tiles:
                            after_attack_tile = min(non_overlapping_zero_tiles, key=lambda item: self.selected_battler.pos.distance_to(pygame.math.Vector2(item)))
                        print("이동 가능한 타일 없음 - 다른 타겟 검색")
                        excluded_targets.add(battler)
                        start_pos = self.selected_battler.pos
                        cur_moves = self.max_moves
                        temp_move_roots = []
                        battler = None
                        continue
                    else:
                        print("이동 가능한 타일 없음 - 다른 타겟 검색")
                        excluded_targets.add(battler)
                        start_pos = self.selected_battler.pos
                        cur_moves = self.max_moves
                        temp_move_roots = []
                        battler = None
                        continue
                    
                    back_tiles = self.map_action.check_movable_from_pos(temp_move_roots[-1], cur_moves, exclude_pos=excluded_list, show=False,check_pos=pygame.math.Vector2(after_attack_tile))
                    
                    if back_tiles:
                        random_back_path = random.choice(back_tiles)
                        back_vector_list = [pygame.math.Vector2(t) for t in random_back_path[1:]]
                        temp_move_roots.extend(back_vector_list)
                        self.result_temp_move_roots = temp_move_roots
                break

        if not temp_move_roots:
            sense_target_list = []
            sense_enemy = self.max_moves + 10
            # print(f"감지 범위: {sense_enemy}")
            diamond = [(dx, dy) for dx in range(-sense_enemy, sense_enemy + 1) 
                    for dy in range(-sense_enemy, sense_enemy + 1) 
                    if abs(dx) + abs(dy) <= sense_enemy]
            
            for dx, dy in diamond:            
                for battler in self.battlersEnemies:
                    if battler.pos == pygame.math.Vector2(self.selected_battler.pos.x+dx,self.selected_battler.pos.y+dy):
                        sense_target_list.append(battler)
            
            if sense_target_list:
                target = max(sense_target_list, key=lambda b: b.stats.get('CHA', 0))
                # print(f"가장 CHA가 높은 타겟: {target.name}, CHA: {target.stats["CHA"]}")
                paths = self.map_action.find_approach_path(self.selected_battler.pos, target.pos, self.max_moves, sense_enemy)
                
                if paths:
                    route = paths[0][1]  # 첫 번째 경로의 위치들
                    
                    # 이동 가능한 범위까지만 경로 자르기
                    total_cost = 0
                    valid_route = []
                    for pos, cost in route[1:]:  # 시작점 제외
                        if cost <= self.max_moves:
                            valid_route.append(pos)
                        else:
                            break
                    # print(route)
                    # 시작점을 제외한 나머지 위치들을 Vector2로 변환
                    temp_move_roots = [pygame.math.Vector2(pos) for pos in valid_route]
                else:
                    print("경로를 찾을 수 없습니다.")
            else:
                print("감지된 타겟이 없습니다.")
                
            # print('접근 모드로 전환')
        self.result_temp_move_roots = temp_move_roots
        return '이동'

    def range_ai(self):
        attack_range = self.char_data["Range"]
        # print(attack_range)
        diamond = [(dx, dy) for dx in range(-attack_range, attack_range + 1) 
                for dy in range(-attack_range, attack_range + 1) 
                if abs(dx) + abs(dy) <= attack_range]
        check_diamond = []
        for tiledxdy in diamond:
            check_tile = self.map_action.get_tiles_in_line(
                self.selected_battler.pos,
                self.selected_battler.pos + pygame.math.Vector2(tiledxdy)
            )
            if all(not tile['blocked'] for tile in check_tile):
                check_diamond.append(self.selected_battler.pos + pygame.math.Vector2(tiledxdy))
        
        attackable_target = []
        Max_CHA = 0
        for searching_target in [battler for battler in self.level.battler_sprites if battler.team != self.selected_battler.team]:
            if any(searching_target.pos == tile for tile in check_diamond) and searching_target.pos != self.selected_battler.pos:
                attackable_target.append(searching_target)
        target_battler = None
        if len(attackable_target) > 1:
            attackable_target = sorted(attackable_target, key=lambda battler: battler.stats["CHA"], reverse=True)
            for target in attackable_target:
                virtual_damage = self.selected_battler.stats["DEX"] + self.selected_battler.stats["STR"] - target.stats["RES"]
                if target.Cur_HP < virtual_damage:
                    target_battler = target
                    break
            if not target_battler:
                for target in attackable_target:
                    virtual_damage = self.selected_battler.stats["DEX"] + self.selected_battler.stats["STR"] - target.stats["RES"]
                    if target.Cur_HP < 2 * virtual_damage:
                        target_battler = target
                        break  
            if not target_battler:
                for target in attackable_target:
                    if target.stats["CHA"] < Max_CHA:
                        continue
                    Max_CHA = target.stats["CHA"]
                    target_battler = target
        elif len(attackable_target):   # 타겟 한명만 잡힐 때
            target_battler = attackable_target[0]
        if target_battler:
            self.map_action.target_battler = target_battler
            # self.level.cursor.rect.center = self.selected_battler.collision_rect.center
            # self.level.cursor = self.selected_battler.pos
            self.level.visible_sprites.focus_on_target(self.selected_battler)
            self.map_action.selected_battler.update_facing_direction(target_battler.pos - self.map_action.selected_battler.pos)
            self.map_action.selected_battler.actlist.append('range_attack')
            self.map_action.update_time = pygame.time.get_ticks() + self.map_action.selected_battler.attack_delay + 500

            return '원거리 공격'
        else: # 접근
            Sense_Enemy = 15
            Sensable_Enemies = []
            for battler in [battler for battler in self.level.battler_sprites if battler.team != self.selected_battler.team]:
                if sum(abs(c) for c in (self.selected_battler.pos - battler.pos)) < Sense_Enemy:
                    Sensable_Enemies.append(battler)
            MAX_CHA_battler = max(Sensable_Enemies, key=lambda battler: battler.stats["CHA"])
            path = self.map_action.find_approach_path(self.selected_battler.pos, MAX_CHA_battler.pos, self.selected_battler.stats["Mov"], Sense_Enemy + 5)
            if path:
                route = path[0][1]  # path[0]은 첫 번째 경로, [1]은 좌표 리스트
                cur_moves = self.selected_battler.stats["Mov"]
                valid_route = []
                # print(path)
                for pos, cost in route[1:]:  # 시작점 제외
                    if cost <= cur_moves and sum(abs(c) for c in (pos - battler.pos)) >= attack_range:
                        # print(self.map_action.get_tiles_in_line(self.selected_battler.pos,self.selected_battler.pos + pygame.math.Vector2(tiledxdy)))
                        valid_route.append(pygame.math.Vector2(pos))
                    else:
                        break
                self.result_temp_move_roots = valid_route
                return '이동'
                
                # 경로가 있으면 실행
                # if self.result_temp_move_roots:
                #     return
            else:
                self.map_action.endturn()
                return '턴종료'
            
    def delete_movable_tiles(self,object,filter_target):
        object_pos_list = {pos for pos, value in filter_target if value != 0}
        return [pos for pos, _ in object if pos not in object_pos_list]

    def execute_move_roots(self):
        if self.result_temp_move_roots:
            end_pos = self.result_temp_move_roots[-1]
            i = 0
            self.map_action.cur_moves = self.selected_battler.stats["Mov"]
            reference_pos = self.map_action.move_roots[-1][0].pos if self.map_action.move_roots else self.selected_battler.pos
            while end_pos != reference_pos:
                move_cost = int(self.level.level_data["moves"][int(self.result_temp_move_roots[i][0])][int(self.result_temp_move_roots[i][1])])
                self.map_action.move_roots.append([Tile((self.result_temp_move_roots[i][0] * TILESIZE, self.result_temp_move_roots[i][1] * TILESIZE),[self.level.visible_sprites, self.level.obstacle_sprites],'move_root'),move_cost])
                self.map_action.cur_moves -= move_cost
                self.map_action.update_path_tiles()
                reference_pos = self.map_action.move_roots[-1][0].pos if self.map_action.move_roots else self.selected_battler.pos
                i += 1
            self.selected_battler.isfollowing_root = True
            self.selected_battler.ismove = True
            return 'player_moving'
        else:
            self.map_action.endturn()
            return '턴종료'

    def magic_ai(self):
        # 1. 시전가능한 스킬 조사
        result = []
        usable_skills = []
        for skill in self.selected_battler.skills:
            if SKILL_PROPERTIES[skill].get('Style') == 'magic' and self.selected_battler.Cur_MP >= SKILL_PROPERTIES[skill]['Mana'][self.selected_battler.skills[skill]]:
                print(f"사용가능한 스킬 {skill},LV.{self.selected_battler.skills[skill]}")
                usable_skills.append(skill)
        if not usable_skills:
            if 'MP_Potion' in self.selected_battler.inventory and self.selected_battler.Cur_MP < self.selected_battler.stats['Max_MP']:
                self.map_action.item_to_use = 'MP_Potion'
                self.map_action.target_battler = self.selected_battler
                return '아이템사용'
            
        for skill in usable_skills:
            skill_info = SKILL_PROPERTIES[skill]
            
            if skill_info['shape'] != 'linear':
                attackable_pos = self.map_action.check_magic_range(self.selected_battler, skill)
                # print(skill,attackable_pos)
                single_kill_targets = []
                double_kill_targets = []
                other_targets = []
                for battler in sorted(self.level.battler_sprites, key=lambda x: x.stats["CHA"], reverse=True):
                    if battler.pos in attackable_pos and istarget(skill, self.selected_battler, battler): #and battler.team != self.selected_battler.team:
                        target_magic_def = battler.stats["INT"] * 1.2 + battler.stats["RES"] * 0.4
                        level_diff_bonus = (self.selected_battler.stats["INT"] - battler.stats["INT"]) * 0.015
                        skill_multiplier = skill_info.get('Dmg_Coff', {}).get(self.selected_battler.skills[skill], 0)
                        virtual_damage = ((1 + level_diff_bonus) * skill_multiplier * 1.5) - target_magic_def

                        if skill_info['skill_type'] == 'Targeting_all':
                            if battler.Cur_HP <= virtual_damage:
                                single_kill_targets.append(battler)
                            elif battler.Cur_HP <= (virtual_damage * 2):
                                double_kill_targets.append(battler)
                            else:
                                other_targets.append(battler)
                        elif skill_info['skill_type'] == 'Targeting':
                            if battler.Cur_HP <= virtual_damage:
                                single_kill_targets = [battler]
                                double_kill_targets = []  # Changed from None to empty list
                                other_targets = []  # Changed from None to empty list
                                break
                            elif battler.Cur_HP <= (virtual_damage * 2):
                                single_kill_targets = []
                                double_kill_targets = [battler]
                                other_targets = []  # Changed from None to empty list
                            else:
                                single_kill_targets = []
                                double_kill_targets = []
                                other_targets = [battler]
                result.append([skill, single_kill_targets, double_kill_targets, other_targets])
                    
            elif skill_info['shape'] == 'linear':
                for facing in ['up','left','down','right']:
                    self.map_action.temp_facing = facing
                    attackable_pos = self.map_action.check_magic_range(self.selected_battler, skill)
                    single_kill_targets = []
                    double_kill_targets = []
                    other_targets = []
                    for battler in sorted(self.level.battler_sprites, key=lambda x: x.stats["CHA"], reverse=True):
                        if battler.pos in attackable_pos and istarget(skill, self.selected_battler, battler): #and battler.team != self.selected_battler.team:
                            target_magic_def = battler.stats["INT"] * 1.2 + battler.stats["RES"] * 0.4
                            level_diff_bonus = (self.selected_battler.stats["INT"] - battler.stats["INT"]) * 0.015
                            skill_multiplier = skill_info.get('Dmg_Coff', {}).get(self.selected_battler.skills[skill], 0)
                            virtual_damage = ((1 + level_diff_bonus) * skill_multiplier * 1.5) - target_magic_def

                            if battler.Cur_HP <= virtual_damage:
                                single_kill_targets.append(battler)
                            elif battler.Cur_HP <= (virtual_damage * 2):
                                double_kill_targets.append(battler)
                            else:
                                other_targets.append(battler)
                    result.append([skill+"_"+facing, single_kill_targets, double_kill_targets, other_targets])
                    
        # print(result)   
        selected_skill = None
        selected_direction = None
        selected_targets = []
        max_targets = 0
        
        for skill_info in result:
            skill_name = skill_info[0]
            # 모든 타겟을 하나의 리스트로 합침 (이제 None 값이 없으므로 안전하게 연결 가능)
            all_targets = skill_info[1] + skill_info[2] + skill_info[3]
            print(skill_name,[target.team for target in all_targets])
            
            if len([target for target in all_targets if target.team != self.selected_battler.team]) > max_targets:
                max_targets = len(all_targets)
                # 방향이 있는 스킬인 경우 분리
                if '_' in skill_name:
                    base_skill, direction = skill_name.rsplit('_', 1)
                    selected_skill = base_skill
                    selected_direction = direction
                else:
                    selected_skill = skill_name
                    selected_direction = None
                selected_targets = all_targets

        if selected_skill and selected_targets:
            # 방향이 있는 경우 설정
            if selected_direction:
                self.map_action.temp_facing = selected_direction
                
            self.map_action.skill = selected_skill
            # Create highlight tiles for the skill
            attackable_pos = self.map_action.check_magic_range(self.selected_battler, selected_skill)
            self.map_action.highlight_tiles_set([pygame.math.Vector2(pos[0], pos[1]) for pos in attackable_pos], mode='Set', color='yellow')
            self.map_action.highlight_tiles_set(None, mode='Invisible')
            self.map_action.target_battler = selected_targets
            return '스킬사용'

        # 2. 시전가능한 스킬이 없으면 아군 무리로 이동
        sense_enemy = 12
        # 공격 대상이 없으면 접근
        sense_target_list = []
        for battler in self.level.battler_sprites:
            if battler.team != self.selected_battler.team:
                distance = abs(battler.pos.x - self.selected_battler.pos.x) + abs(battler.pos.y - self.selected_battler.pos.y)
                if distance <= sense_enemy:
                    sense_target_list.append(battler)
        if sense_target_list:
            target = max(sense_target_list, key=lambda b: b.stats['CHA'])
            paths = self.map_action.find_approach_path(self.selected_battler.pos, target.pos, self.selected_battler.stats['Mov'], sense_enemy)
            if paths:
                route = paths[0][1]
                valid_route = [pygame.math.Vector2(pos) for pos, cost in route[1:] if cost <= self.selected_battler.stats['Mov']]
                if valid_route:
                    self.result_temp_move_roots = valid_route
                    return '이동'
            return '턴종료'
        
        # 아이템도 없으면 아군 무리로 이동
        ally_positions = [battler.pos for battler in self.level.battler_sprites if battler.team == self.selected_battler.team and battler != self.selected_battler]
        if ally_positions:
            closest_ally_pos = min(ally_positions, key=lambda pos: self.selected_battler.pos.distance_to(pos))
            paths = self.map_action.find_approach_path(self.selected_battler.pos, closest_ally_pos, self.selected_battler.stats['Mov'], sense_enemy)
            if paths:
                route = paths[0][1]
                valid_route = [pygame.math.Vector2(pos) for pos, cost in route[1:] if cost <= self.selected_battler.stats['Mov']]
                if valid_route:
                    self.result_temp_move_roots = valid_route
                    return '이동'
            return '턴종료'
        
        # 아군 무리도 없으면 도망
        enemy_positions = [battler.pos for battler in self.level.battler_sprites if battler.team != self.selected_battler.team]
        if enemy_positions:
            farthest_enemy_pos = max(enemy_positions, key=lambda pos: self.selected_battler.pos.distance_to(pos))
            paths = self.map_action.find_approach_path(self.selected_battler.pos, farthest_enemy_pos, self.selected_battler.stats['Mov'], sense_enemy)
            if paths:
                route = paths[0][1]
                valid_route = [pygame.math.Vector2(pos) for pos, cost in route[1:] if cost <= self.selected_battler.stats['Mov']]
                if valid_route:
                    self.result_temp_move_roots = valid_route
                    return '이동'
            return '턴종료'
        return '턴종료'

    def execute(self):
        self.battler_init()
        # print(self.char_data)
        if self.selected_battler.force_inactive or self.selected_battler.inactive:
            result = '턴종료'
        elif self.char_data['Class'] == 'Melee':
            result = self.melee_ai()
        elif self.char_data['Class'] == 'Range':
            result = self.range_ai()
        elif self.char_data['Class'] == 'Magic':
            result = self.magic_ai()
        # print(result)
        if result == '이동':
            self.execute_move_roots()
            return 'player_moving'
        elif result == '스킬사용':
            return 'interact','skill0'
        elif result == '아이템사용':
            return 'interact','using_item1'
        elif result == '턴종료':
            self.map_action.endturn()
        elif result == '원거리 공격':
            return 'interact','range0'
        else:
            return result
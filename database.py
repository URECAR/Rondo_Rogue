# Database.py
from properties import *
import random
class MAP1:
    data = {
        'Max_X' : 35 * TILESIZE,
        'Max_Y' : 25 * TILESIZE,   
    }
    spawns = {
        'Player1': {'Spawn': [14, 14], 'Level': 3, 'base_team': 'Ally'},
        'Player2': {'Spawn': [14, 13], 'Level': 4, 'base_team': 'Ally'},
        'Player3': {'Spawn': [15, 14], 'Level': 4, 'base_team': 'Ally'},
        'Player_wizard1': {'Spawn': [13, 14], 'Level': 3, 'base_team': 'Ally'},
        'Spirit': {'Spawn': [10, 13], 'Level': 5, 'base_team': 'Enemy'},
        'Army_Archer': {'Spawn': [9, 14], 'Level': 6, 'base_team': 'Enemy'},
        'Piglin': {'Spawn': [12, 14], 'Level': 6, 'base_team': 'Enemy'},
        'Bamboo': {'Spawn': [13, 20], 'Level': 6, 'base_team': 'Enemy'}
    }
class CharacterDatabase:
    data = {
        'Player1': {
            'name'  : '푸른파수꾼',
            'base_stats': {
                'Max_HP': 192, 'Max_MP': 35, 'STR': 24, 'DEX': 18, 'INT': 18, 'RES': 25,
                'CHA': 25, 'Max_EXP': 30, 'Mov': 5
            },
            'growth_stats': {
                # 기본 성장률
                'default': {'Max_HP': 8, 'Max_MP': 4, 'Max_EXP': 3, 'STR': 0.5, 'DEX': 0.5, 'INT': 0.5, 'RES': 0.7,},
                'level_ranges': [
                    {'range': (10, 20), 'Max_HP': 10, 'STR': 0.7, 'RES': 0.8},
                    {'range': (20, 30), 'Max_HP': 12, 'STR': 0.8, 'DEX': 0.7}
                ]
            },
            'graphics': {
                'graphics_folder': '../graphics/player1',
                'has_directions': True,
                'animation_types': ['idle', 'move', 'selected', 'casting','attack','range'],
                'animation_speed': {
                    'idle': 16,      # idle_anime_tick
                    'move': 16,      # move_anime_tick
                    'selected': 12,  # selected_anime_tick
                    'attack': 10,    # attack_anime_tick
                    'casting': 16,   # casting_anime_tick
                    'range': 16      # range_anime_tick
                },
                'move_speed': 8,
                'die_animation': 'SPREAD_LINE',
                'attack_delay': 300,
                'attack_afterdelay': 200,
                'size': 2.0,  # 2배 크기
                'offset': [0, -32]  # 중앙에서 위로 16픽셀 이동
            },
            'Class': 'Melee',
            'equips' : [
                # '절망','안아줘요 날다람쥐','러시안룰렛', '도윤이의 풍선자동차'
                        ],
            # 'Range' : 6,
            'inventory': ['HP_Potion', 'MP_Potion', 'Shield_Potion','Battle_Potion'],
            'skills': {
                '불굴의 의지' : 1,
                # '무념의 기보' : 1,
                '체력 단련' : 3,
                '아이스1' : 1,
                '아이스2' : 1,
                '번개 마법1' : 1,
                # '오버드라이브1' : 1,
                '근접 방어 태세' : 1,
                '테스트스킬3' : 1,
                '힐링' : 1,
                # '테스트스킬5' : 1,
                '상시 근접 방어' : 1,
                '저돌맹진' : 1,
                '무념의 기보' : 3,
                # 'Z.O.C 무시' : 1,
                '신중함' : 3,
            },
            'OverDrive' : {                 # select_OV_Target 함수로 사용 진행. 
                'skill' : '오버드라이브1',
                'max_level' : 3,
                'charge_speed' : [1,1],     # 본인이 입은 데미지 비율 * charge_speed[0] + 상대방에게 입힌 데미지 비율 * charge_speed[1]
            },
        },
        'Player2': {
            'name'  : '밀키스',
            'base_stats': {
                'Max_HP': 204, 'Max_MP': 5, 'STR': 20, 'DEX': 10, 'INT': 13, 'RES': 20,
                'CHA': 30, 'Max_EXP': 30, 'Mov': 5
            },
            'growth_stats': {
                # 기본 성장률
                'default': {'Max_HP': 5, 'Max_MP': 3, 'STR': 0.5, 'DEX': 0.5, 'INT': 0.5, 'RES': 0.5},
                'level_ranges': [
                    {'range': (10, 20), 'Max_HP': 8, 'STR': 0.8},
                    {'range': (20, 30), 'Max_HP': 10, 'STR': 1.0, 'DEX': 0.7}
                ]
            },
            'graphics': {
                'graphics_folder': '../graphics/player2',
                'has_directions': True,
                'animation_types': ['idle', 'move', 'selected', 'casting','attack'],
                'animation_speed': {
                    'idle': 16,      # idle_anime_tick
                    'move': 16,      # move_anime_tick
                    'selected': 12,  # selected_anime_tick
                    'attack': 10,    # attack_anime_tick
                    'casting': 16,   # casting_anime_tick
                    'range': 16      # range_anime_tick
                },
                'move_speed': 8,
                'die_animation': 'SPREAD_LINE',
                'attack_delay': 100,
                'attack_afterdelay': 400,
                'size': 2.0,  # 2배 크기
                'offset': [0, -32]  # 중앙에서 위로 16픽셀 이동

            },
            'Class': 'Melee',
            'equips' : [],
            'inventory': [],
            'skills': {
                '전장의 함성' : 1,
                '전장의 질주' : 1,
                '전장의 찬가' : 1,
                '보좌' : 1,
            },
        },
        'Player3': {
            'name'  : '덩굴정령',
            'base_stats': {
                'Max_HP': 150, 'Max_MP': 20, 'STR': 12, 'DEX': 25, 'INT': 8, 'RES': 12,
                'CHA': 25, 'Max_EXP': 30, 'Mov': 10
            },
            'growth_stats': {
                # 기본 성장률
                'default': {'Max_HP': 5, 'Max_MP': 4, 'Max_EXP': 3, 'STR': 0.5, 'DEX': 0.5, 'INT': 0.5, 'RES': 0.5,},
                'level_ranges': [
                    {'range': (10, 20), 'Max_HP': 8, 'STR': 0.8},
                    {'range': (20, 30), 'Max_HP': 10, 'STR': 1.0, 'DEX': 0.7}
                ]
            },
            'graphics': {
                'graphics_folder': '../graphics/player3',
                'has_directions': True,
                'animation_types': ['idle', 'move', 'selected', 'casting','range'],
                'move_speed': 8,
                'die_animation': 'SPREAD_LINE',
                'attack_delay': 400,
                'attack_afterdelay': 100,
                'size': 1.0,  # 2배 크기
            },
            'equips' : ['절망'],
            'Class': 'Range',
            'Range' : 6,
            'inventory': ['HP_Potion', 'MP_Potion', 'Shield_Potion'],
            'skills': {
                # '강력' : 1,
                # 'Z.O.C': 1,
                # '아이스1': 1,
                # '아이스2': 1,
                # '불 마법1': 1,
                # '테스트스킬3': 1,
                # '근접 방어 태세': 1,
                # '테스트스킬5': 2,
                # '신중함' : 3,
                # '힐링' : 2,
            },
        },
        'Player_wizard1': {
            'name'  : '이안',
            'base_stats': {
                'Max_HP': 85, 'Max_MP': 70, 'STR': 5, 'DEX': 8, 'INT': 28, 'RES': 7,
                'CHA': 20, 'Max_EXP': 30, 'Mov': 4
            },
            'growth_stats': {
                # 기본 성장률
                'default': {'Max_HP': 3, 'Max_MP': 4, 'Max_EXP': 3, 'STR': 0.5, 'DEX': 0.5, 'INT': 0.7, 'RES': 0.5,},
                'level_ranges': [
                    {'range': (10, 20), 'Max_MP': 6, 'INT': 0.9},
                    {'range': (20, 30), 'Max_MP': 9, 'INT': 1.1}
                ]
            },
            'graphics': {
                'graphics_folder': '../graphics/player_wizard1',
                'has_directions': True,
                'animation_types': ['idle', 'move', 'selected', 'casting'],
                'move_speed': 8,
                'die_animation': 'SPREAD_LINE',
                # 'attack_delay': 400,
                # 'attack_afterdelay': 100,
                'size': 4.0,
                'offset' : [0,-36]
            },
            'equips' : ['희망'],
            'Class': 'Magic',
            'inventory': ['HP_Potion', 'MP_Potion', 'Shield_Potion'],
            'skills': {
                # '강력' : 1,
                # 'Z.O.C': 1,
                '아이스1': 1,
                # '아이스2': 1,
                '불 마법1': 1,
                '힐링' : 1,
                '마력 운용' : 1,
            },
        },
        'Spirit': {
            'name'  : '솔의 눈',
            'base_stats': {
                'Max_HP': 7, 'Max_MP': 60, 'STR': 18, 'DEX': 20, 'INT': 80, 'RES': 7,
                'CHA': 25, 'Max_EXP': 30, 'Mov': 6
            },
            'growth_stats': {
                # 기본 성장률
                'default': {'Max_HP': 5, 'Max_MP': 3, 'STR': 0.5, 'DEX': 0.5, 'INT': 0.5, 'RES': 0.5},
                'level_ranges': [
                    {'range': (10, 20), 'Max_HP': 8, 'STR': 0.8},
                    {'range': (20, 30), 'Max_HP': 10, 'STR': 1.0, 'DEX': 0.7}
                ]
            },
            'graphics': {
                'graphics_folder': '../graphics/monsters/spirit',
                'has_directions': False,
                'animation_types': ['idle', 'move'],
                'die_animation': 'DEAD_SPARK',
                'attack_delay': 200,
                'attack_afterdelay': 200,
            },
            'Class': 'Magic',
            'inventory': ['MP_Potion'],
            'skills': {
                '임기응변': 2,
                '아이스1' : 2,
                '아이스2' : 1,
                '불 마법1' : 1,
            },
            'hidden_stats': ['STR', 'Mov'],
            'Kill_EXP': 30,
            # ''
        },
        'Bamboo': {
            'name'  : '대나 무',
            'base_stats': {
                'Max_HP': 50, 'Max_MP': 1, 'STR': 4, 'DEX': 4, 'INT': 4, 'RES': 4,
                'CHA': 25, 'Max_EXP': 30, 'Mov': 5
            },
            'growth_stats': {
                # 기본 성장률
                'default': {'Max_HP': 5, 'Max_MP': 3, 'STR': 0.5, 'DEX': 0.5, 'INT': 0.5, 'RES': 0.5},
                'level_ranges': [
                    {'range': (10, 20), 'Max_HP': 8, 'STR': 0.8},
                    {'range': (20, 30), 'Max_HP': 10, 'STR': 1.0, 'DEX': 0.7}
                ]
            },
            'graphics': {
                'graphics_folder': '../graphics/monsters/bamboo',
                'has_directions': False,
                'animation_types': ['idle', 'move'],
                'die_animation': 'DEAD_SMOKE',
                'attack_delay': 200,
                'attack_afterdelay': 200,
                
            },
            'Class': 'Melee',
            'skills': {
            },
            'hidden_stats': ['DEX', 'INT'],
            'Kill_EXP': 30,
        }, 
        'Piglin': {
            'name'  : '피글 린',
            'base_stats': {
                'Max_HP': 120, 'Max_MP': 1, 'STR': 23, 'DEX': 4, 'INT': 4, 'RES': 16,
                'CHA': 25, 'Max_EXP': 30, 'Mov': 4
            },
            'growth_stats': {
                # 기본 성장률
                'default': {'Max_HP': 5, 'Max_MP': 3, 'STR': 0.5, 'DEX': 0.5, 'INT': 0.5, 'RES': 0.5},
                'level_ranges': [
                    {'range': (10, 20), 'Max_HP': 8, 'STR': 0.8},
                    {'range': (20, 30), 'Max_HP': 10, 'STR': 1.0, 'DEX': 0.7}
                ]
            },
            'graphics': {
                'graphics_folder': '../graphics/monsters/piglin',
                'has_directions': True,
                'animation_types': ['idle', 'move','attack'],
                'die_animation': 'DEAD_SMOKE',
                'attack_delay': 200,
                'attack_afterdelay': 200,
                'size' : 2,
                'offset': [0, -32]  # 중앙에서 위로 16픽셀 이동

            },
            'Class': 'Melee',
            'skills': {
                'Z.O.C' : 1,
            },
            'hidden_stats': ['STR', 'RES'],
            'Kill_EXP': 40,
        },
        'Army_Archer': {
            'name'  : '병사 궁병',
            'base_stats': {
                'Max_HP': 120, 'Max_MP': 1, 'STR': 15, 'DEX': 25, 'INT': 8, 'RES': 15,
                'CHA': 25, 'Max_EXP': 30, 'Mov': 3
            },
            'growth_stats': {
                # 기본 성장률
                'default': {'Max_HP': 5, 'Max_MP': 3, 'STR': 0.5, 'DEX': 0.5, 'INT': 0.5, 'RES': 0.5},
                'level_ranges': [
                    {'range': (10, 20), 'Max_HP': 8, 'STR': 0.8},
                    {'range': (20, 30), 'Max_HP': 10, 'STR': 1.0, 'DEX': 0.7}
                ]
            },

            'graphics': {
                'graphics_folder': '../graphics/monsters/army_archer',
                'has_directions': True,
                'animation_types': ['idle', 'move','range','hit'],
                'die_animation': 'DEAD_SMOKE',
                'animation_speed': {
                    'attack': 30,    # attack_anime_tick
                    'casting': 16,   # casting_anime_tick
                    'range': 16      # range_anime_tick
                },
                'attack_delay': 200,
                'attack_afterdelay': 200,
                'size' : 2,
                'offset': [0, -32]  # 중앙에서 위로 16픽셀 이동

            },
            'Class': 'Range',
            'equips' :['롱 보우'],
            'Range' : 7,
            'skills': {
                # 'Z.O.C' : 1,
            },
            'hidden_stats': ['DEX', 'INT'],
            'Kill_EXP': 30,
        },        
    }
    @staticmethod
    def get_character_data(char_type):
        if char_type not in CharacterDatabase.data:
            raise ValueError(f"Character type '{char_type}' not found in database")
        return CharacterDatabase.data[char_type]
    @staticmethod 
    def calculate_stats(char_type, level):
        if char_type not in CharacterDatabase.data:
            raise ValueError(f"Character type '{char_type}' not found")
        char_data = CharacterDatabase.data[char_type]
        base_stats = char_data['base_stats'].copy()
        growth = char_data['growth_stats'] 
        # 레벨별 구간에 따른 스탯 계산
        for stat, base_value in base_stats.items():
            if stat in growth['default']:
                total_growth = 0
                current_level = 1
                # 레벨 구간별 성장 계산
                for range_data in growth.get('level_ranges', []):
                    range_start, range_end = range_data['range']
                    
                    # 현재 레벨이 이 구간에 도달하기 전
                    if level <= range_start:
                        total_growth += (level - current_level) * growth['default'][stat]
                        break
                    
                    # 이 구간의 성장 계산
                    if current_level < range_start:
                        total_growth += (range_start - current_level) * growth['default'][stat]
                        current_level = range_start
                    
                    # 구간 내 성장
                    if level <= range_end:
                        total_growth += (level - current_level) * range_data.get(stat, growth['default'][stat])
                        break
                    else:
                        total_growth += (range_end - current_level) * range_data.get(stat, growth['default'][stat])
                        current_level = range_end
                
                # 남은 레벨 처리
                if level > current_level:
                    total_growth += (level - current_level) * growth['default'][stat]
                
                base_stats[stat] += total_growth
        # stats에 combat_stats 추가
        combat_stats = {
            'Melee_atk_mul': 1.0,   'Melee_def_mul': 1.0,
            'Magic_atk_mul': 1.0,   'Magic_def_mul': 1.0,
            'Ranged_atk_mul': 1.0, 'Ranged_def_mul': 1.0,
            'Frontal_atk_mul': 1.0, 'Side_atk_mul': 1.0, 'Rear_atk_mul': 1.0,
            'Frontal_def_mul': 1.0, 'Side_def_mul': 1.0, 'Rear_def_mul': 1.0,
            'HP_Regen': 0, 'MP_Regen': 0,
            'HP_Regen%': 0, 'MP_Regen%': 0,
            'Accuracy_rate': 1.0, 
            'Critical_Chance' : 0, 'Critical_atk_mul' : 2.0,
            'Melee_evasion_chance': 0, 'Ranged_evasion_chance': 0,
            'Counter_Chance': 0, 'Counter_atk_mul': 1.0, 'ZOC_Chance': 0, 'ZOC_Ignore_Chance' : 0,
            'CHA_increase_mul' : 1.0,
            'EXP_mul' : 1.0, 'Level_Up_Regen' : 0,
            'OVD_charge_rate' : 1.0
        }
        base_stats.update(combat_stats)  # stats에 combat_stats 통합
        return base_stats
class CombatFormulas:
    def calculate_melee_damage(attacker, target, Damage_Bonus_multiplier, is_critical):
        """근접 공격 데미지 계산 공식"""
        base_damage = (attacker.stats['STR'] * 2 - target.stats['RES'])
        multiplier = attacker.stats['Melee_atk_mul'] * target.stats['Melee_def_mul'] * Damage_Bonus_multiplier
        if is_critical:
            multiplier *= attacker.stats['Critical_atk_mul']
        Final_Damage = int(max(base_damage * multiplier, 0))
        return Final_Damage

    def calculate_range_damage( attacker, target, is_critical):
        """원거리 공격 데미지 계산 공식"""
        base_damage = (attacker.stats['STR'] + attacker.stats['DEX'] - target.stats['RES'])
        multiplier = attacker.stats['Ranged_atk_mul'] * target.stats['Ranged_def_mul']
        if is_critical:
            multiplier *= attacker.stats['Critical_atk_mul']
        Final_Damage = int(max(base_damage * multiplier, 0))
        return Final_Damage

    def calculate_magic_damage(attacker, defender, skill_name, skill_level):
        """마법 공격 데미지 계산 공식"""
        skill_info = SKILL_PROPERTIES[skill_name]['Active']
        
        target_magic_def = defender.stats["INT"] * 0.2 + defender.stats["RES"] * 0.4
        stat_diff_bonus = (attacker.stats["INT"] - defender.stats["INT"]) * 0.015
        skill_multiplier = skill_info['damage'].get('dmg_coef', {}).get(skill_level, 0)
        Final_Damage = int(max(((1 + stat_diff_bonus) * skill_multiplier * 1.5) - target_magic_def, 0))
        return Final_Damage

    def calculate_melee_counter_damage(self,attacker,target):
        Counter_damage = int((target.stats['DEX'] + target.stats['STR'] - attacker.stats["RES"]) * target.stats["Melee_atk_mul"] * attacker.stats["Melee_def_mul"] * target.stats["Counter_atk_mul"])
        self.map_action.Acted.append([attacker,'Counter_Damage_Calculated', Counter_damage])
        return Counter_damage

    def calculate_heal(self,caster,target,skill_name,skill_level):
        skill_info = SKILL_PROPERTIES[skill_name]
        heal_amount = skill_info['Heal'][skill_level] + caster.stats["INT"]
        self.map_action.Acted.append([target,'Heal_Calculated',heal_amount])
        return heal_amount
        
    def check_melee_counter(self, attacker, target, vurnerable):
        total_counter_chance = (target.stats["Counter_Chance"] + (target.stats["DEX"] - attacker.stats["DEX"]) * 0.5 - vurnerable["counter"]) * 0.01
        self.map_action.Acted.append([target,'Counter_Check',total_counter_chance])
        if total_counter_chance > random.random():
            self.map_action.Acted.append([target,'Counter_Check',[total_counter_chance,'Executed']])
            return True
        else:
            return False 

    def check_melee_evasion(self, attacker, target, vurnerable):
        total_hit_chance = attacker.stats["Accuracy_rate"]+( ((attacker.stats["DEX"] - target.stats["DEX"]) * 2  - target.stats["Melee_evasion_chance"] + vurnerable["evasion"]) * 0.01)
        if total_hit_chance < random.random():
            self.map_action.Acted.append([target,'Hit_Check','Evaded'])
            return True 
        else:
            return False

    def check_range_evasion(self, attacker, target):
        total_accuracy = (attacker.stats["Accuracy_rate"] - target.stats["Ranged_evasion_chance"] +(attacker.stats["DEX"] - target.stats["DEX"]) * 0.02)
        self.map_action.Acted.append([target,'Hit_Check','Executed'])
        if total_accuracy < random.random():
            self.map_action.Acted.append([target,'Hit_Check','Evaded'])
            return True
        else:
            self.map_action.Acted.append([target,'Hit_Check','Executed'])
            return False

    def check_melee_critical(self, attacker, target, vurnerable):
        total_crit_chance = (attacker.stats["Critical_Chance"] + attacker.stats["DEX"] * 0.5 + vurnerable['critical']) * 0.01
        self.map_action.Acted.append([target,'Critical_Check',total_crit_chance])
        if total_crit_chance > random.random():
            self.map_action.Acted.append([target,'Critical_Check','Executed'])
            return True
        else:
            return False

    def check_range_critical(self, attacker, target):
        total_crit_chance = (attacker.stats["Critical_Chance"] + attacker.stats["DEX"] * 0.6) * 0.01
        self.map_action.Acted.append([target,'Critical_Check',total_crit_chance])
        if total_crit_chance > random.random():
            self.map_action.Acted.append([target,'Critical_Check','Executed'])
            return True
        else:
            return False
                
    def check_ZOC(self, attacker, target, vurnerable, is_critical):
        total_zoc_check = (target.stats["ZOC_Chance"] - attacker.stats["ZOC_Ignore_Chance"] - vurnerable['zoc']) * 0.01
        self.map_action.Acted.append([target,'ZOC_Check',total_zoc_check])    
        if target.Cur_HP > 0 and random.random() < total_zoc_check and not is_critical:
            self.map_action.Acted.append([target,'ZOC_Check','Executed'])
            return True
        else:
            return False

    def calculate_directional_bonus(attacker, target):
        opposite_directions = {"left": "right", "right": "left", "up": "down"}
        hit_location = 'rear' if target.facing == attacker.facing else 'side' if target.facing != opposite_directions.get(attacker.facing) else 'front'
        hit_stats = {
                    'front': {'mul': 1.0 * attacker.stats['Frontal_atk_mul'] * target.stats['Frontal_def_mul'], 'vurnerable': {'zoc': 5, 'evasion': 0, 'counter': 0, 'critical': 0}},
                    'side': {'mul': 1.1 * attacker.stats['Side_atk_mul'] * target.stats['Side_def_mul'], 'vurnerable': {'zoc': 10, 'evasion': 5, 'counter': 5, 'critical': 4}},
                    'rear': {'mul': 1.25 * attacker.stats['Rear_atk_mul'] * target.stats['Rear_def_mul'], 'vurnerable': {'zoc': 15, 'evasion': 15, 'counter': 15, 'critical': 8}}
                }
        bonuses = hit_stats[hit_location]
        Damage_Bonus_multiplier = bonuses['mul']
        vurnerable = bonuses['vurnerable']
        return Damage_Bonus_multiplier, vurnerable

    def ZOC_status_check():
        return 0.2
ANIMATION_PROPERTIES = {
    'SLASH': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/slash',
        'size': 2,
        'anchor': 'center',
        'sound': 'ATTACK_SLASH'
    },
    'CRITICAL': {
        'frame_speed': 15,
        'folder_path': '../graphics/particles/critical',
        'size': 1,
        'anchor': 'center',
        'sound': 'CRITICAL'
    },
    'HEAL': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/heal',
        'size': 1,
        'anchor': 'center',
    },
    'RANGE_HIT': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/range',
        'size': 2,
        'anchor': 'center',
        'offset': [0,-20],
        'sound': 'ATTACK_ARROW'
    },
#------------------------------#
    'EMOTE_DESPAIR': {
        'frame_speed': 5,
        'folder_path': '../graphics/particles/emotion/despair',
        'size': 2,
        'anchor': 'top',
    },    
    'EMOTE_SURPRISE': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/emotion/surprise',
        'size': 2,
        'anchor': 'top',
    },
#------------------------------#
    'ATTACK_ENHANCE': {
        'frame_speed': 50,
        'folder_path': '../graphics/particles/attack_enhance',
        'size': 2,
        'anchor': 'center',
    },
    'SHIELD': {
        'frame_speed': 50,
        'folder_path': '../graphics/particles/shield',
        'size': 2,
        'anchor': 'center',
        'offset' : [0,-20],
        'sound': 'SHIELD'
    },
    'SHIELD2': {
        'frame_speed': 10,
        'folder_path': '../graphics/particles/shield2',
        'size': 4,
        'anchor': 'center',
        'sound': 'SHIELD',
        'priority_offset': 64,
    },
    'HOLY': {
        'frame_speed': 15,
        'folder_path': '../graphics/particles/aura',
        'size': 1,
        'anchor': 'center',
        'priority_offset': 64,
    },
    'AURA': {
        'frame_speed': 15,
        'folder_path': '../graphics/particles/aura',
        'size': 1,
        'anchor': 'center',
        'priority_offset': 64,
    },
    'HOLY_LIGHT': {
        'frame_speed': 15,
        'folder_path': '../graphics/particles/holy_light',
        'size': 4,
        'anchor': 'center',
        'priority_offset': 64,
        'offset':[0,-128]
    },
    'HOLY_CROSS': {
        'frame_speed': 15,
        'folder_path': '../graphics/particles/holy_cross',
        'size': 1,
        'anchor': 'center',
        'priority_offset': 64,
    },
    'ICE1': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/ice',
        'size': 1,
        'anchor': 'bottom',
        'offset': [0, -48],
        'sound': 'ICE_MAGIC1'
    },
    'ICE2': {
        'frame_speed': 10,
        'folder_path': '../graphics/particles/icicle',
        'size': 3,
        'anchor': 'bottom',
        'offset': [0, -16],
        'sound': 'ICE_MAGIC1'
    },
    'FIRE1': {
        'frame_speed': 30,
        'folder_path': '../graphics/particles/fire',
        'size': 1,
        'anchor': 'bottom',
        'offset': [0, -64],
        'priority_offset': 64,
        'sound': 'FIRE_MAGIC1'
    },
    'THUNDER1': {
        'frame_speed': 10,
        'folder_path': '../graphics/particles/thunder',
        'size': 1,
        'anchor': 'bottom',
        'offset': [0,-40],
    },
    'MAGIC_CIRCLE': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/magic_circle1',
        'size': 1.5,
        'anchor': 'bottom',
        'offset': [32,50],
        'sound': 'MAGIC_CAST',
        'priority_offset': -1,
    },
    'MAGIC_CIRCLE2': {
        'frame_speed': 30,
        'folder_path': '../graphics/particles/magic_circle2',
        'size': 1,
        'anchor': 'bottom',
        'offset': [32,-8],
        'sound': 'MAGIC_CAST',
        'priority_offset': -1,
    },
    'DEAD_SMOKE': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/smoke',
        'size': 2,
        'anchor': 'center',
        'character_invisible': True,
    },
    'DEAD_SPARK': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/sparkle',
        'size': 2,
        'anchor': 'center',
        'character_invisible': True,
    },
    'SPREAD_LINE': {
        'split_time': 1.0,
        'split_speed': 120,
        'size': 5,
        'anchor': 'center',
        'character_invisible': True,
    },
    'DAMAGE': {
        'size': 1,
        'anchor': 'center',
        'duration': 1.0,            # 전체 애니메이션 시간
        'horizontal_speed': 50,     # x축 이동 속도
        'initial_velocity': -150,   # 초기 수직 속도 (음수는 위로 향함)
        'gravity': 400             # 중력 가속도
    },
    'CRITICAL_DAMAGE': {
        'size': 1,
        'anchor': 'center',
        'duration': 1.0,            # 전체 애니메이션 시간
        'horizontal_speed': 50,     # x축 이동 속도
        'initial_velocity': -150,   # 초기 수직 속도 (음수는 위로 향함)
        'gravity': 400             # 중력 가속도
    },
    'ITEM_HEAL': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/heal',
        'size': 1,
        'anchor': 'center',
    },
    'POTION': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/heal',
        'size': 1,
        'anchor': 'center',
        'sound': 'POTION',
        'priority_offset': 64,
    },
    'PHASE_CHANGE': {
        'size': 0.5,                # 화면 크기 대비 백분율 (size_fit_screen이 False일 때 사용)
        'size_fit_screen': False,   # True면 화면에 맞게, False면 size 비율 사용
        'anchor': 'center',
        'duration': 1.0,           # 전체 애니메이션 시간
        'center_duration': 0.6,    # 중앙에 머무는 시간
        'start_scale': 0.5,        # 시작할 때의 크기 비율
        'slide_speed': 400,        # 이동 속도
        'fade_in_duration': 0.2,   # 페이드 인 시간
        'fade_out_duration': 0.2,  # 페이드 아웃 시간
        'folder_path': '../graphics/UI',  # 이미지 경로
    },
    'STAT_CHANGE': {
        'size': 1,
        'anchor': 'center',
        'duration': 1.0,
        'rise_speed': 30, 
        'fade_in': 0.2,
        'fade_out': 0.3,
        'font_size': 18,
        'font_color': (255, 255, 255),
        'bg_color': (0, 0, 0, 128),
        'bg_padding': (8, 4)
    },
    'LEVEL_UP': {
        'size': 1,
        'anchor': 'center',
        'duration': 2.0,
        'rise_height': 50,
        'fade_in': 0.3,
        'fade_out': 0.5,
        'font_size': 24,
        'font_color': (255, 255, 100),  # 밝은 노란색
        'glow_color': (255, 200, 0, 128),  # 반투명한 주황빛
        'sound': 'LEVEL_UP',
    },
}
SKILL_PROPERTIES = {
    # 기본 스킬 템플릿
    'SKILL_TEMPLATE_설명': {
        # 필수 속성
        'Type': '',           ## Passive / Active
        'Description': '',    ## 스킬 설명 (
        'Style' : 'default',    # 스킬 UI에서의 색상 표시(default, magic, support, red, purple. 추후 스타일 수정 예정)
        # 패시브 스킬 속성
        'Passive': {
            'effect_type': '',    ## constant(상시 적용) / conditional(조건 적용) / support(응원 적용) 
            'condition': {        # conditional일 경우 사용
                'target': '',     # self / allies / enemies
                'stat': '',       # 체크할 스탯 (activate_condition 또는 stats에서 체크)
                'check_type': [], # ['equal', 'more', 'less'] 중 해당되는 것들
                'threshold': {},  # 검사
                  
            },
            'support': {          # support일 경우 사용
                'target': '',          # owner(이 배틀러가 효과 받음) / passer(지나가는 배틀러가 효과 받음)
                'effect_source': '',   # owner(이 배틀러의 스탯 사용) / passer(지나가는 배틀러의 스탯 사용)
                'effect_type': '',     # buff(이동 동안만 유지) / immediate(즉시 적용)
                'animation': '',       # 효과 받을 때의 애니메이션 타입
            },
            'effects': {        # 패시브 스탯이 존재할 경우 사용
                'stats'  : {},     # 스탯 증가
                'stats_%': {},
                'status' : {},    # 상태이상 부여
            }
        },
    
        # 액티브 스킬 속성
        'Active': {
            'type': 'magic',        ## skill / magic / overdrive
            'skill_type' : '',      ## attack / support / heal / buff / buff_temp / debuff / summon
            
            # 범위 관련
            'range_type' : '',      # diamond / linear / cross / square / ...
            'range': {},            # 레벨별 사거리
            'target_team': [],      # Self(자신) / Ally(자신을 제외한 아군) / Enemy(적군)
            'target_option' : '',   # one / all / part
            'area' : {},            # 타격 범위
            
            # 시전 관련
            'mp_cost': {},      # 레벨별 MP 소모량  (0일 경우 소거가능)
    
            # 애니메이션 관련
            'cast_animation': '', # 시전 애니메이션
            'effect_animation': '', # 효과 애니메이션
            # 'hit_animation': '',   # 타격 애니메이션
            'Dmg_timing': 0,     # 데미지 적용 타이밍
            'animate_type' : '', # default(대상 타일에 1회), all_tiles(모든 타일에 1회), sequential(모든 타일을 특정 순서대로), target(지정 타일에 1회)
            'sequential' : {
              'tick' : 0,
            },    
            # 효과 관련
            'damage': {
                'dmg_type': '',  # physical / magical / heal / None
                'dmg_coef': {},      # 레벨별 기본 데미지
            },
            'damage_divide' : {
                'enable' : False,
                'damage_divided_count' : 0,  # 타격 시 데미지 분할 여부
                'divide_tick' : 0,
                },
            'effects': {
                'stats' : {},     # 고정 스탯 변화량
                'stats_%' : {},   # 퍼센트 스탯 변화량
                'status' : {},    # 상태이상 및 확률
                'duration': 0,    # 지속시간 (턴)
            }
        }
    },
    # --- 패시브 --- #
    'Z.O.C': {
        'Type': 'Passive',
        'Description': '보유 시, 상대의 이동을 일정 확률로 저지한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'ZOC_Chance': 50},
                    2: {'ZOC_Chance': 70},
                    3: {'ZOC_Chance': 90},
                },
            },
        },
    },
    'Z.O.C 무시': {
        'Type': 'Passive',
        'Description': '보유 시, 상대의 저지를 무시할 확률이 생긴다.',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'ZOC_Ignore_Chance': 35},
                    2: {'ZOC_Ignore_Chance': 60},
                    3: {'ZOC_Ignore_Chance': 75},
                },
            },
        },
    },
    '상시 근접 방어': {
        'Type': 'Passive',
        'Description': '보유 시, 받는 근접 피해량%을 줄인다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats_%': {
                    1: {'Melee_def_mul': -40},
                    2: {'Melee_def_mul': -60},
                    3: {'Melee_def_mul': -70},
                },
            },
        },
    },
    '임기응변': {
        'Type': 'Passive',
        'Description': '보유 시, 반격율이 상승한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'Counter_Chance': 5},
                    2: {'Counter_Chance': 10},
                    3: {'Counter_Chance': 15},
                },
            },
        },
    },
    '저돌맹진': {
        'Type': 'Passive',
        'Description': '보유 시 STR%이 상승하지만, RES%가 하락한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                
                'stats_%': {
                    1: {'STR': 10, 'RES': -10},
                    2: {'STR': 15, 'RES': -15},
                    3: {'STR': 20, 'RES': -20},
                },
                
            },
        },
    },
    '강력': {
        'Type': 'Passive',
        'Description': '보유 시 STR% 가 증가한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                
                'stats_%': {
                    1: {'STR': 20},
                    2: {'STR': 40},
                    3: {'STR': 60},
                },
                
            },
        },
    },
    # 단순 스탯 증가
    '무도의 진수': {
        'Type': 'Passive',
        'Description': '보유 시 STR이 상승한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'STR': 3},
                    2: {'STR': 6},
                    3: {'STR': 9},
                },
            },
        },
    },
    '만색의 예지': {
        'Type': 'Passive',
        'Description': '보유 시 INT가 상승한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'INT': 3},
                    2: {'INT': 6},
                    3: {'INT': 9},
                },
            },
        },  
    },
    
    # 단순 스탯 % 증가
    '견고': {
        'Type': 'Passive',
        'Description': '보유 시 RES% 가 증가한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                
                'stats_%': {
                    1: {'RES': 20},
                    2: {'RES': 40},
                    3: {'RES': 60},
                },
                
            },
        },
    },
    '신중함': {
        'Type': 'Passive',
        'Description': '보유 시 명중률이 상승한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'Accuracy_rate': 0.1},
                    2: {'Accuracy_rate': 0.2},
                    3: {'Accuracy_rate': 0.3},
                },
                
            },
        },
    },
    '축지의 비기': {
        'Type': 'Passive',
        'Description': '보유 시 이동력이 증가한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'Mov': 1},
                    2: {'Mov': 2},
                    3: {'Mov': 3},
                },
                
            },
        },
    },
    '체력 단련': {
        'Type': 'Passive',
        'Description': '보유 시 최대 HP%가 상승한다.',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                
                'stats_%': {
                    1: {'Max_HP': 10},
                    2: {'Max_HP': 20},
                    3: {'Max_HP': 30},
                },
                
            },
        },
    },
    '마력 운용': {
        'Type': 'Passive',
        'Description': '보유 시 최대 MP%가 상승한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                
                'stats_%': {
                    1: {'Max_MP': 15},
                    2: {'Max_MP': 30},
                    3: {'Max_MP': 50},
                },
                
            },
        },
    },
    '인과응보': {
        'Type': 'Passive',
        'Description': '보유 시 반격 데미지가 상승한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                
                'stats_%': {
                    1: {'Counter_atk_mul': 15},
                    2: {'Counter_atk_mul': 30},
                    3: {'Counter_atk_mul': 45},
                },
                
            },
        },
    },
    '라이온 하트': {
        'Type': 'Passive',
        'Description': '보유 시 CHA 상승률이 증가한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                
                'stats_%': {
                    1: {'CHA_increase_mul': 15},
                    2: {'CHA_increase_mul': 30},
                    3: {'CHA_increase_mul': 45},
                },
                
            },
        },
    },
    '회피기동': {
        'Type': 'Passive',
        'Description': '보유 시 회피율이 증가한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'Melee_evasion_rate': 15},
                    2: {'Melee_evasion_rate': 30},
                    3: {'Melee_evasion_rate': 45},
                    },
                
            },
        },
    },
    '야전 의료': {
        'Type': 'Passive',
        'Description': '보유 시 HP %를 지속적으로 회복한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'HP_Regen%': 3},
                    2: {'HP_Regen%': 6},
                    3: {'HP_Regen%': 9},
                },
                
            },
        },
    },
    '마력 반환': {
        'Type': 'Passive',
        'Description': '보유 시 MP %를 지속적으로 회복한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'MP_Regen%': 3},
                    2: {'MP_Regen%': 6},
                    3: {'MP_Regen%': 9},
                },
                
            },
        },
    },
    '아마데우스': {
        'Type': 'Passive',
        'Description': '보유 시 경험치 획득량 %이 증가한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                
                'stats_%': {
                    1: {'EXP_mul': 10},
                    2: {'EXP_mul': 20},
                    3: {'EXP_mul': 3000},
                },
                
            },
        },
    },
    '다시 불타는 혼': {
        'Type': 'Passive',
        'Description': '보유 시 레벨업 시 HP,MP %를 추가로 회복한다',
        'Style': 'default',
        'Passive': {
            'effect_type': 'constant',
            'effects': {
                'stats': {
                    1: {'Level_Up_Regen': 10},
                    2: {'Level_Up_Regen': 20},
                    3: {'Level_Up_Regen': 30},
                    },
                
            },
        },
    },
    # --- 패시브 - 응원형 --- #
    '보좌': {   
        'Type': 'Passive',           
        'Description': '보유 시, 지나가는 아군의 HP를 회복시켜준다.',  
        'Style' : 'default',    
        'Passive': {
            'effect_type': 'support',   
            'support': {         
                'target': 'passer',         
                'effect_source': 'owner',  
                'effect_type': 'immediate',    
                'animation': 'HEAL',   
            },    
            'effects': {
                'stats': {
                    1 : {'Cur_HP' : 10},
                    2 : {'Cur_HP' : 20},
                    3 : {'Cur_HP' : 30},
                    },     
                   
            },
        },
    },    
    '전장의 함성': {    
        'Type': 'Passive',          
        'Description': '''보유 시 자신을 지나는 아군의 STR을 해당 이동 페이즈에만 자신의 STR의 일정 수치만큼 증가시킨다''',    
        'Style' : 'default',   
        'Passive': {
            'effect_type': 'support',    
            'support': {         
                'target': 'passer',          
                'effect_source': 'owner', 
                'effect_type': 'buff',    
                'animation': 'AURA',      
            },
            'effects': {
                    
                'stats_%': {   
                    1: {'STR' : 5},
                    2: {'STR' : 10},
                    3: {'STR' : 15},
                        },    
                   
            },
        },
    },
    '전장의 질주': {    # 지나는 순간 그 이동 동안만 크리티컬율 증가 버프
        'Type': 'Passive',          
        'Description': '''보유 시, 자신을 지나는 아군의 크리티컬율을 해당 이동 페이즈에만 증가시킨다''',    
        'Style' : 'default',   
        'Passive': {
            'effect_type': 'support',    
            'support': {         
                'target': 'passer',          
                'effect_source': 'owner', 
                'effect_type': 'buff',    
                'animation': 'AURA',      
            },
            'effects': {
                'stats': {    
                    1: {'Critical_Chance' : 5},
                    2: {'Critical_Chance' : 10},
                    3: {'Critical_Chance' : 15},
                        },    
                   
            },
        },
    },
    '전장의 찬가': {    # 
        'Type': 'Passive',          
        'Description': '''보유 시 자신을 지나는 아군의 주는 근접데미지를 해당 이동 페이즈에만 증가시킨다''',    
        'Style' : 'default',   
        'Passive': {
            'effect_type': 'support',    
            'support': {         
                'target': 'passer',          
                'effect_source': 'owner', 
                'effect_type': 'buff',    
                'animation': 'AURA',      
            },
            'effects': {
                'stats': {    
                    1: {'Melee_atk_mul' : 0.05},
                    2: {'Melee_atk_mul' : 0.1},
                    3: {'Melee_atk_mul' : 0.15},
                        },    
                   
            },
        },
    },
    # --- 패시브 - 조건부 --- #
    '무념의 기보': {
        # 필수 속성
        'Type': 'Passive',
        'Description': '보유 시 {threshold}턴 동안 마법을 사용하지 않을 시 Mov가 1 상승한다.',
        'Style' : 'purple', 
        # 패시브 스킬 속성
        'Passive': {
            'effect_type': 'conditional',
            'condition': {     
                'target': 'self',  
                'stat': 'Turn_Without_Magic',  
                'check_type': ['Equal','More'],
                'threshold': {   
                    1: 4,
                    2: 3,
                    3: 2,
                    },   
            },
            'effects': {
                'stats': {
                    1 : {'Mov' : 1},
                    2 : {'Mov' : 1},
                    3 : {'Mov' : 1},
                    },     
            }
        },
    },
    '불굴의 의지': {
        'Type': 'Passive',
        'Description': '보유 시 HP가 {threshold}% 이하이면 STR%이 증가한다.',
        'Style' : 'red',
        # 패시브 스킬 속성
        'Passive': {
            'effect_type': 'conditional', 
            'condition': { 
                'target': 'self',  
                'stat': 'HP_ratio',  
                'check_type': ['Equal','Less'], 
                'threshold': {
                    1: 50,
                    2: 50,
                    3: 50,
                    }, 
                  
            },
            'effects': {
                'stats_%': {
                    1 : {'STR' : 10},
                    2 : {'STR' : 15},
                    3 : {'STR' : 20},
                    },
            }
        },
    },
    # --- 버프 --- #
    '테스트스킬3': {

        'Type': 'Active',  
        'Description': '사용 시, 다음 자신 페이즈까지 RES%를 올린다',  
        'Style' : 'purple',  
        'Active': {
            'type': 'skill',   
            'skill_type' : 'buff_temp',

            'target_team': ['Self'], 
            'target_option' : 'one',

            'cast_animation': 'MAGIC_CIRCLE', 
            'effect_animation': 'AURA', 
            'animate_type' : 'default', 

            'effects': {
                'stats_%': {  
                    1: {'RES': 20},
                    2: {'RES': 40},
                    3: {'RES': 60},
                    },   
                'duration': 3   
            }
        }
    },
    '근접 방어 태세': {
        # 필수 속성
        'Type': 'Active',    
        'Description': '사용 시, 다음 자신 페이즈까지 받는 근접 피해량%을 줄인다',  
        'Style' : 'purple', 
        # 액티브 스킬 속성
        'Active': {
            'type': 'skill',  
            'skill_type' : 'buff_temp',
            'range_type' : '',  
            'range': {},        
            'target_team': ['Self'],    
            'target_option' : 'one',
            'area' : {},        
            'mp_cost': {}, 
            'cast_animation': 'MAGIC_CIRCLE',
            'effect_animation': 'AURA',
            'animate_type' : 'default', 
            'effects': {
                'stats': { 
                    1: {'Melee_def_mul' : -0.4},
                    2: {'Melee_def_mul' : -0.6},
                    3: {'Melee_def_mul' : -0.7},
                },
                'duration': 3 
            },
        }
    },

    # --- 액티브 - 매직 스킬 --- #
    '아이스1': {
        'Type': 'Active',      
        'Description': '{range}칸 내 하나에게 얼음 공격을 가한다', 
        'Style' : 'magic', 
        'Active': {
            'type': 'magic', 
            'skill_type' : '',
            'range_type' : 'diamond', 
            'range': {1:4, 2:5, 3:6},   
            'target_team': ['Ally','Enemy'],  
            'target_option' : 'one', 

            'mp_cost': {1:20, 2:25, 3:30}, 
            'cast_animation': 'MAGIC_CIRCLE2', 
            'effect_animation': 'ICE2',
            'Dmg_timing': 400,
            'animate_type' : 'default',
            'damage': {
                'dmg_type': 'magical',
                'dmg_coef': {1:35, 2:45, 3:60},
            },
            'effects': {
                'status': {1: {'동결' : 10}, 2: {'동결' : 10}, 3: {'동결' : 10},},
                'duration': 2 
            }
        }
    },
    '아이스2': {
        'Type': 'Active', 
        'Description': '전방 {range}칸 내의 모두에게 얼음 공격을 가한다',
        'Style' : 'magic',
        'Active': {
            'type': 'magic',
            'skill_type' : '',
            'range_type' : 'linear', 
            'range': {1:5, 2:6, 3:7}, 
            'target_team': ['Ally','Enemy'],
            'target_option' : 'all',
            'mp_cost': {1:20, 2:25, 3:30}, 
    
            # 애니메이션 관련
            'cast_animation': 'MAGIC_CIRCLE2',
            'effect_animation': 'ICE2', 
            'Dmg_timing': 400,
            'animate_type' : 'all_tiles', 
            'damage': {
                'dmg_type': 'magical',
                'dmg_coef': {1:35, 2:45, 3:60},
            },
            'effects': {
                'status': {1: {'동결' : 10}, 2: {'동결' : 10}, 3: {'동결' : 10},},
                'duration': 2 
            }
        }
    },
    '번개 마법1': {
        'Type': 'Active', 
        'Description': '{range}칸 내 자신을 제외한 모두에게 번개를 소환한다',
        'Style' : 'magic',
        'Active': {
            'type': 'magic',
            'skill_type' : '',
            'range_type' : 'diamond',
            'range': {1:3, 2:4, 3:5},
            'target_team': ['Ally','Enemy'],
            'target_option' : 'all',
            'mp_cost': {1:20, 2:25, 3:30}, 
            'cast_animation': 'MAGIC_CIRCLE2',
            'effect_animation': 'THUNDER1', 
            'Dmg_timing': 400,
            'animate_type' : 'default',
            'damage': {
                'dmg_type': 'magical',
                'dmg_coef': {1:40, 2:50, 3:60},
            },
            'effects': {
                'status': {1: {'약화' : 30}, 2: {'약화' : 40}, 3: {'약화' : 50},},
                'duration': 2
            }
        }
    },
    '불 마법1': {
        'Type': 'Active', 
        'Description': '전방 {range}칸 내의 모두에게 불 공격을 한다.',
        'Style' : 'magic',
        'Active': {
            'type': 'magic',
            'skill_type' : 'attack',    
            'range_type' : 'linear',
            'range': {            
                1: 5,
                2: 6,
                3: 7,
                },
            'target_team': ['Ally','Enemy'],
            'target_option' : 'all',
            'mp_cost': {            
                1: 20,
                2: 25,
                3: 30,
                },
            'cast_animation': 'MAGIC_CIRCLE',
            'effect_animation': 'FIRE1',
            'Dmg_timing': 0.4,
            'animate_type' : 'sequential',
            'sequential' : {
              'tick' : 0.15,
            },    
            'damage': {
                'dmg_type': 'magical',
                'dmg_coef': {1:35, 2:45, 3:60},
            },
            'damage_divide' : {
                'enable' : False,
                'damage_divided_count' : 0,
                'divide_tick' : 0,
                },
            'effects': {
            }
        }
    },

    '오버드라이브1': {
        'Type': 'Active',  
        'Description': '{range}칸 내의 2칸 이내 지역에 빛 공격을 한다.',
        'Style' : 'red',
        'Active': {
            'type': 'overdrive',
            'skill_type' : 'attack',
            'range_type' : 'diamond',  
            'range': {            
                1: 4,
                2: 5,
                3: 6,
                },   
            'area' : {
                'type' : 'diamond',
                'range' : {
                    1: 2,
                    2: 2,
                    3: 2},
            },
            'target_team': ['Self','Ally','Enemy'], 
            'target_option' : 'part', 
            'cast_animation': 'MAGIC_CIRCLE',
            'effect_animation': 'HOLY_LIGHT',
            'Dmg_timing': 1200,
            'animate_type' : 'target', 
            'damage': {
                'dmg_type': 'magical',
                'dmg_coef': {1:60, 2:80, 3:110},
            },

        }
    },
    # --- 액티브 - 서포트 스킬 --- #
    '힐링': {
        'Type': 'Active',
        'Description': '아군 한 명의 체력을 회복시킨다.',
        'Style' : 'support',
        'Active': {
            'type': 'magic',
            'skill_type' : 'heal',
            'range_type' : 'diamond',
            'range': {            
                1: 2,
                2: 3,
                3: 3
                },
            'target_team': ['Ally'],
            'target_option' : 'one',
            'mp_cost': {
                1: 30,
                2: 40,
                3: 50
                },
    
            # 애니메이션 관련
            'cast_animation': 'MAGIC_CIRCLE2',
            'effect_animation': 'HOLY_CROSS',
            'Dmg_timing': 500,
            'animate_type' : 'default',
            'damage': {
                'dmg_type': 'heal',
                'dmg_coef': {
                    1:25,
                    2:40,
                    3:60
                    },
                },
            'effects': {
                'duration': 0
            }
        }
    },

}
STATUS_PROPERTIES = {
    '여기어디': {
        'Description': '몸이 휘청거려 공격력과 이동력이 감소한다.',
        'Notification': '혼란에 빠짐',
        'duration': 3,  # 지속 턴 수
        'Stat_%': {  # 퍼센트 기반 스탯 변화
            'STR': -20,  # -20%
        },
        'Stat': {    # 고정값 스탯 변화
            'Mov': -1,
        }
    },
    '약화': {
        'Description': '힘이 빠져 공격력이 감소한다.',
        'Notification': '약화됨',
        'duration': 3,  # 지속 턴 수
        'Stat_%': {
            'STR': -30,
        }
    },
    '동결': {
        'Description': '몸이 얼어붙어 움직일 수 없다.',
        'Notification': '동결됨',
        'duration': 2,  # 지속 턴 수
        'Stat_%': {},  # 스탯 변화 없음
        'Stat': {},
        'Effects': [
            'inactive',
            'force_hit_melee',
            'force_hit_ranged',
        ],
    },
}
ITEM_PROPERTIES = {
    'HP_Potion': {
        'name': 'HP 포션',
        'Description': '''체력을 최대 체력의 30% 회복시킨다''',
        'Type': 'Active',
        'animate': 'AURA',
        'icon_path': '../graphics/icons/items/potion1.png',
        'Effect': {
            'Heal_%': {'Cur_HP': 30}  # 퍼센트 기반 회복
        }
    },
    'MP_Potion': {
        'name': 'MP 포션',
        'Description': '''MP를 50 회복시킨다''',
        'Type': 'Active',
        'animate': 'AURA',
        'icon_path': '../graphics/icons/items/potion2.png',
        'Effect': {
            'Heal': {'Cur_MP': 50}  # 고정값 회복
        }
    },
    'Shield_Potion': {
        'name': '방어력 포션',
        'Description': '''3턴간 방어력이 10 상승한다''',
        'Type': 'Buff',
        'animate': 'POTION',
        'icon_path': '../graphics/icons/items/potion3.png',
        'Effect': {
            'Buff': {'RES': 10},
            'duration': 3
        }
    },
    'Battle_Potion': {
        'name': '투사의 물약',
        'Description': '''해당 전투 동안 카리스마가 20 상승한다''',
        'Type': 'Permanent',
        'animate': 'AURA',
        'icon_path': '../graphics/icons/items/potion4.png',
        'Effect': {
            'Change': {'CHA': 20}
        }
    },
}
EQUIP_PROPERTIES = {
    '문래자이아파트' : {
        'Description' : '''STR를 10 증가시키지만 RES가 3 감소한다.''',
        'STAT' : {'STR' : 10, 'RES' : -3},
    },
    '러시안룰렛' : {
        'Description' : '''STR가 10 감소하지만 크리티컬 확률이 10% 증가한다. ''',
        'STAT' : {'STR' : -10, 'Critical_Chance' : 10},
    },
    '안아줘요 날다람쥐' : {
        'Description' : '''움직임이 날렵해져, Mov가 1 증가하고 RES가 10 증가한다.''',
        'STAT' : {'Mov' : 1, 'RES' : 10},
    },
    '희망' : {
        'Description' : '''CHA가 20 증가하며, 주는 근접,마법,원거리 데미지 피해량이 10% 증가한다.''',
        'STAT' : {'CHA' : 20, 'Melee_atk_mul' : 10, 'Range_atk_mul' : 10, 'Magic_atk_mul' : 10,},
    },
    '절망' : {
        'Description' : '''CHA가 20 감소하며, 주는 근접,마법,원거리 데미지 피해량이 20% 증가한다.''',
        'STAT' : {'CHA' : -20, 'Melee_atk_mul' : 20, 'Range_atk_mul' : 20, 'Magic_atk_mul' : 20,},
    },
    '강아지 이모티콘' : {
        'Description' : '''반격률이 20% 증가한다.''',
        'STAT' : {'Counter_Chance' : 20},
    },
    '돼지전사의 몽둥이' : {
        'Description' : '''"야야 무겁다 내려놔라"''',
        'STAT' : {'STR' : 10},
    },
    '롱 보우' : {
        'Description' : '''아주 먼 곳을 쏠 수 있을 거 같지만 견디는 힘이 약해 그러진 못한다.''',
        'STAT' : {},
    },
    '도윤이의 풍선자동차' : {
        'Description' : '''후후 불면 달려간다''',
        'STAT' : {},
    },

}
CARD_PROPERTIES = {
    'Common': [
        {'title': '무도의 진수',
         'desc': 'STR이 3 증가한다. ',
            'act': {
                'skill': {'무도의 진수': 1}
            }
         },
        {'title': '만색의 예지',
         'desc': 'INT가 3 증가한다. ',
         'act': {
             'skill': {'만색의 예지': 1}
             }
         },
        {'title': '신중함',
         'desc': '명중률이 10% 증가한다.',
        'act': {
            'skill': {'신중함': 1}
            }
        },
        {'title': '인과응보',
         'desc': '반격 데미지가 15% 증가한다.',
         'act': {
             'skill': {'인과응보': 1}
             }
         },
        {'title': '라이온 하트',
         'desc': 'CHA 상승률이 15% 증가한다.',
         'act': {
             'skill': {'라이온 하트': 1}
             }
         },

        {'title': '아마데우스',
         'desc': '경험치 획득량 %이 증가한다.',
         'act': {
             'skill': {'아마데우스': 1}
             }
         },
        
    ],
    'Uncommon': [
        {'title': '체력 단련',
         'desc': '최대 HP가 10% 증가한다.',
         'act': {
             'skill': {'체력 단련': 1}
             }
         },
        {'title': '마력 운용',
         'desc': '최대 MP가 15% 증가한다.',
         'act': {
             'skill': {'마력 운용': 1}
             }
         },
        {'title': '강력',
         'desc': 'STR이 20% 증가한다.',
         'act': {
             'skill': {'강력': 1}
             }
         },
        {'title': '견고',
         'desc': 'RES가 20% 증가한다.',
         'act': {
             'skill': {'견고': 1}
             }
         },
        {'title': '축지의 비기',
         'desc': '이동력이 1 증가한다.',
         'act': {
             'skill': {'축지의 비기': 1}
             }
         },
        {'title': '야전 의료',
         'desc': 'HP %를 지속적으로 회복한다.',
         'act': {
             'skill': {'야전 의료': 1}
             }
         },
                {'title': '회피기동',
         'desc': '회피율이 15% 증가한다.',
         'act': {
             'skill': {'회피기동': 1}
             }
         },
        {'title': '마력 반환',
         'desc': 'MP %를 지속적으로 회복한다.',
         'act': {
             'skill': {'마력 반환': 1}
             }
         },
    ],
    'Rare': [
        {'title': '생명의 축복',
         'desc': '최대 HP가 25% 증가하고, 매 턴마다 HP가 2% 회복된다.',
         'act': {
             'skill': {'생명의 축복': 1}
             }
         },
        {'title': '마력의 지배자',
         'desc': '최대 MP가 30% 증가하고, 스킬 소모 MP가 15% 감소한다.',
         'act': {
             'skill': {'마력의 지배자': 1}
             }
         },
        {'title': '전투의 대가',
         'desc': 'STR이 35% 증가하고, 크리티컬 확률이 10% 증가한다.',
         'act': {
             'skill': {'전투의 대가': 1}
             }
         },
        {'title': '불굴의 의지',
         'desc': 'RES가 35% 증가하고, 받는 피해가 10% 감소한다.',
         'act': {
             'skill': {'불굴의 의지': 1}
             }
         },
        {'title': '현자의 지혜',
         'desc': 'INT가 35% 증가하고, 모든 속성 피해가 15% 증가한다.',
         'act': {
             'skill': {'현자의 지혜': 1}
             }
         },
        {'title': '카리스마의 귀공',
         'desc': 'CHA가 35% 증가하고, 아군 버프 효과가 20% 증가한다.',
         'act': {
             'skill': {'카리스마의 귀공': 1}
             }
         }
    ],
}
SOUND_PROPERTIES = {
    'CURSOR_CLICK': {
        'path': '../audio/SE/cursor_select.mp3',
        'volume': 0.5,
        'delay': 0,
    },
    'CURSOR_SELECT': {
        'path': '../audio/SE/cursor_select.mp3',
        'volume': 1.0,
        'delay': 0,
    },
    'CURSOR_MOVE': {
        'path': '../audio/SE/cursor_move.ogg',
        'volume': 0.5,
        'delay': 0,
    },
    'CURSOR_CANCEL': {
        'path': '../audio/SE/cursor_cancel.ogg',
        'volume': 0.5,
        'delay': 0,
    },
    'MENU_SELECT': {
        'path': '../audio/SE/cursor_select.mp3',
        'volume': 0.5,
        'delay': 0,
    },
    'MENU_MOVE': {
        'path': '../audio/SE/cursor_move.ogg',
        'volume': 0.4,
        'delay': 0,
    },
    # 전투 사운드
    'ATTACK_SLASH': {
        'path': '../audio/SE/slash_1.ogg',
        'volume': 1.0,
        'delay': 0,
    },
    'CRITICAL': {
        'path': '../audio/SE/critical.wav',
        'volume': 1.0,
        'delay': 0,
    },
    'ATTACK_ARROW': {
        'path': '../audio/SE/arrow_attacked.mp3',
        'volume': 1.0,
        'delay': 0,
    },
    'ARROW_FLYING': {
        'path': '../audio/SE/arrow_flying.mp3',
        'volume': 1.0,
        'delay': 0.5,
    },
    'SHOOT_ARROW': {
        'path': '../audio/SE/shoot_arrow.mp3',
        'volume': 0.8,
        'delay': 0.4,
    },
    'EVASION': {
        'path': '../audio/SE/evasion_1.ogg',
        'volume': 0.7,
        'delay': 0,
    },
    'SHIELD': {
        'path': '../audio/SE/guard_1.mp3',
        'delay': 0.0,
        'volume': 1.0,
    },
    # 스킬/마법 사운드
    'MAGIC_CAST': {
        'path': '../audio/SE/magic_circle.ogg',
        'volume': 0.8,
        'delay': 0.2,
    },
    'ICE_MAGIC1': {
        'path': '../audio/SE/ice_1.ogg',
        'volume': 1.0,
        'delay': 0.2,
    },
    'FIRE_MAGIC1': {
        'path': '../audio/SE/fire_1.ogg',
        'volume': 1.0,
        'delay': 0,
    },
    'POTION': {
        'path': '../audio/SE/아이템 섭취.mp3',
        'volume': 0.8,
        'delay': 0,
    },
        # 시스템 사운드
    'LEVEL_UP': {
        'path': '../audio/SE/level_up.ogg',
        'volume': 0.7,
        'delay': 0,
    },
    'EVASION': {
        'path': '../audio/SE/evasion_1.ogg',
        'volume': 0.5,
        'delay': 0,
    },
        # BGM
    'ALLY_PHASE': {
        'path': '../audio/BGM/Ally2.mp3',
        'volume': 1.0,
        'loop': True
    },
    'ENEMY_PHASE': {
        'path': '../audio/BGM/Enemy.mp3',
        'volume': 1.0,
        'loop': True
    },
}
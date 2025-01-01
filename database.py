# Database.py
from properties import *

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
                '절망','안아줘요 날다람쥐','러시안룰렛', '도윤이의 풍선자동차'
                        ],
            # 'Range' : 6,
            'inventory': ['HP_Potion', 'MP_Potion', 'Shield_Potion','Battle_Potion'],
            'skills': {
                '아이스' : 1,
                '테스트스킬1' : 1,
                '테스트스킬2' : 1,
                '테스트스킬3' : 1,
                '테스트스킬5' : 1,
                '상시 근접 방어' : 1,
                '저돌맹진' : 1,
                '무념의 기보' : 3,
                'Z.O.C 무시' : 1,
                '신중함' : 3,
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
                'attack_delay': 400,
                'attack_afterdelay': 100,
                'size': 2.0,  # 2배 크기
                'offset': [0, -32]  # 중앙에서 위로 16픽셀 이동

            },
            'Class': 'Melee',
            'equips' : [],
            'inventory': [],
            'skills': {

            },
        },
        'Player3': {
            'name'  : '덩굴정령',
            'base_stats': {
                'Max_HP': 150, 'Max_MP': 20, 'STR': 12, 'DEX': 25, 'INT': 8, 'RES': 12,
                'CHA': 25, 'Max_EXP': 30, 'Mov': 5
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
                # '아이스': 1,
                # '테스트스킬1': 1,
                # '테스트스킬2': 1,
                # '테스트스킬3': 1,
                # '근접 방어 태세': 1,
                # '테스트스킬5': 2,
                # '신중함' : 3,
                # '군의학' : 2,
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
                '아이스': 1,
                '테스트스킬1': 1,
                '테스트스킬5': 1,
                '군의학' : 2,
                '마력 운용' : 1,
            },
        },
        'Spirit': {
            'name'  : '솔의 눈',
            'base_stats': {
                'Max_HP': 7, 'Max_MP': 1, 'STR': 18, 'DEX': 200, 'INT': 20, 'RES': 7,
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
            'inventory': [],
            'skills': {
                '임기응변': 2,
                '아이스' : 2,
            },
            'hidden_stats': ['STR', 'Mov'],
            'Kill_EXP': 30,
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
        combat_stats = {
            'Melee_attack_multiplier': 1.0,   'Melee_defense_multiplier': 1.0,
            'Magic_attack_multiplier': 1.0,   'Magic_defense_multiplier': 1.0,
            'Ranged_attack_multiplier': 1.0, 'Ranged_defense_multiplier': 1.0,
            'Frontal_attack_multiplier': 1.0, 'Side_attack_multiplier': 1.0, 'Rear_attack_multiplier': 1.0,
            'HP_Regen': 0, 'MP_Regen': 0,
            'HP_Regen%': 0, 'MP_Regen%': 0,
            'Accuracy_rate': 1.0, 
            'Critical_Chance' : 0, 'Critical_attack_multiplier' : 2.0,
            'Melee_evasion_chance': 0, 'Ranged_evasion_chance': 0,
            'Counter_Chance': 0, 'Counter_attack_multiplier': 1.0, 'ZOC_Chance': 0, 'ZOC_Ignore_Chance' : 0,
            'CHA_increase_multiplier' : 1.0,
            'EXP_multiplier' : 1.0, 'Level_Up_Regen' : 0,
        }
        base_stats.update(combat_stats)  # stats에 combat_stats 통합
        return base_stats
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
        'folder_path': '../graphics/particles/heal/frames',
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
    'AURA': {
        'frame_speed': 15,
        'folder_path': '../graphics/particles/aura',
        'size': 1,
        'anchor': 'center',
        'track_target' : True,
    },
    'ICE1': {
        'frame_speed': 10,
        'folder_path': '../graphics/particles/ice',
        'size': 1,
        'anchor': 'bottom',
        'offset': [0, -48],
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
        'folder_path': '../graphics/particles/magic_circle',
        'size': 1.5,
        'anchor': 'bottom',
        'offset': [32,50],
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
    'ITEM_HEAL': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/heal/frames',
        'size': 1,
        'anchor': 'center',
    },
    'POTION': {
        'frame_speed': 20,
        'folder_path': '../graphics/particles/heal/frames',
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
    # --- 패시브 --- #
    'Z.O.C': {
        'name': 'Zone of Control',
        'Type': 'Passive',
        'Description': '''보유 시, 상대의 이동을 일정 확률로 저지한다''',
        'Status_%': {
            1: {'여기어디': 20},
            2: {'여기어디': 20},
            3: {'여기어디': 20},
        },
        'Buff': {
            1: {'ZOC_Chance': 50},
            2: {'ZOC_Chance': 70},
            3: {'ZOC_Chance': 90},
        },
    },
    'Z.O.C 무시': {
        'name': 'Ignore Zone of Control',
        'Type': 'Passive',
        'Description': '''보유 시, 상대의 저지를 무시할 확률이 생긴다.''',

        'Buff': {
            1: {'ZOC_Ignore_Chance': 35},
            2: {'ZOC_Ignore_Chance': 60},
            3: {'ZOC_Ignore_Chance': 75},
        },
    },
    '상시 근접 방어': {
        'name': 'Always Melee Defense',
        'Type': 'Passive',
        'Description' : '''보유 시, 받는 근접 피해량%을 줄인다''',
        'skill_type' : 'Passive',

        'Buff_%': {
            1: {'Melee_defense_multiplier' : -40},
            2: {'Melee_defense_multiplier' : -60},
            3: {'Melee_defense_multiplier' : -70},
        },
    },
    '임기응변': {
        'name': 'Improvisation',
        'Type': 'Passive',
        'Description': '''보유 시, 반격율이 상승한다''',
        'Buff': {
            1: {'Counter_Chance': 5},
            2: {'Counter_Chance': 10},
            3: {'Counter_Chance': 15},
        },
    },
    '저돌맹진': {
        'name': 'Reckless Charge',
        'Type': 'Passive',
        'Description': '''보유 시 STR%이 상승하지만, RES%가 하락한다''',
        'Buff_%': {
            1: {'STR': 10,'RES' : -10},
            2: {'STR': 15,'RES' : -15},
            3: {'STR': 20,'RES' : -20},
        },
    },
    '보좌': {
        'name': 'Support',
        'Type': 'Passive',
        'Support_type' : 'Recovery',
        'Description' : '''보유 시, 자신을 지나는 아군의 HP를 회복시킨다''',
        'Support': {
            1: {'Cur_HP': 5},
            2: {'Cur_HP': 10},
            3: {'Cur_HP': 15},
        },
    },
    '전장의 함성': {
        'name': 'Battle Cry',
        'Type': 'Passive',
        'Support_type' : 'Boost',
        'Description' : '''보유 시 자신을 지나는 아군의 ATK를 해당 이동 페이즈에만 자신의 STR의 일정 수치만큼 증가시킨다''',
        'Support_%': {
            1: {'STR': 5},
            2: {'STR': 10},
            3: {'STR': 15},
        },
    },
    '전장의 질주': {
        'name': 'Battle Rush',
        'Type': 'Passive',
        'Support_type' : 'Boost_self',
        'Description' : '''보유 시, 자신을 지나는 아군의 크리티컬율을 해당 이동 페이즈에만 증가시킨다''',
        'Support': {
            1: {'Critical_Chance': 5},
            2: {'Critical_Chance': 10},
            3: {'Critical_Chance': 15},
        },
    },
    '전장의 찬가': {
        'name': 'Battle Hymn',
        'Type': 'Passive',
        'Support_type' : 'Boost_self',
        'Description' : '''보유 시 자신을 지나는 아군의 주는 근접데미지를 해당 이동 페이즈에만 증가시킨다''',
        'Support_%': {
            1: {'Melee_attack_multiplier': 5},
            2: {'Melee_attack_multiplier': 10},
            3: {'Melee_attack_multiplier': 15},
        },
    },
    '강력': {
        'name': 'Powerful',
        'Type': 'Passive',
        'Description' : '''보유 시 STR% 가 증가한다''',
        'Buff_%': {
            1: {'STR': 20},
            2: {'STR': 40},
            3: {'STR': 60},
        }
    },
    '견고': {
        'name': 'Solid',
        'Type': 'Passive',
        'Description' : '''보유 시 RES% 가 증가한다''',
        'Buff_%': {
            1: {'RES': 20},
            2: {'RES': 40},
            3: {'RES': 60},
        }
    },
    '신중함': {
        'name': 'Caution',
        'Type': 'Passive',
        'Description': '''보유 시 명중률이 상승한다''',
        'Buff': {
            1: {'Accuracy_rate': 10},
            2: {'Accuracy_rate': 20},
            3: {'Accuracy_rate': 30},
        },
    },
    '축지의 비기': {
        'name': 'Secret of Shrinking Earth',
        'Type': 'Passive',
        'Description': '''보유 시 명중률이 상승한다''',
        'Buff': {
            1: {'Mov': 1},
            2: {'Mov': 2},
            3: {'Mov': 3},
        },
    },
    '체력 단련': {
        'name': 'Physical Training',
        'Type': 'Passive',
        'Description': '''보유 시 최대 HP가 상승한다.''',
        'Buff_%': {
            1: {'Max_HP': 10},  # 10% 증가
            2: {'Max_HP': 20},  # 20% 증가
            3: {'Max_HP': 30},  # 30% 증가
        }
    },
    '마력 운용': {
        'name': 'Mana Management',
        'Type': 'Passive',
        'Description': '''보유 시 최대 MP가 상승한다''',
        'Buff_%': {
            1: {'Max_MP': 15},  # 15% 증가
            2: {'Max_MP': 30},  # 30% 증가
            3: {'Max_MP': 50},  # 50% 증가
        }
    },
    '인과응보': {
        'name': 'Retribution',
        'Type': 'Passive',
        'Description': '''보유 시 반격 데미지가 상승한다''',
        'Buff_%': {
            1: {'Counter_attack_multiplier': 15}, 
            2: {'Counter_attack_multiplier': 30}, 
            3: {'Counter_attack_multiplier': 45},  
        }
    },
    '라이온 하트': {
        'name': 'Lion Heart',
        'Type': 'Passive',
        'Description': '''보유 시 CHA 상승률이 증가한다''',
        'Buff_%': {
            1: {'CHA_increase_multiplier': 15}, 
            2: {'CHA_increase_multiplier': 30}, 
            3: {'CHA_increase_multiplier': 45},  
        }
    },
    '회피기': {
        'name': 'Evasion',
        'Type': 'Passive',
        'Description': '''보유 시 회피율이 증가한다''',
        'Buff_%': {
            1: {'Melee_evasion_rate': 15}, 
            2: {'Melee_evasion_rate': 30}, 
            3: {'Melee_evasion_rate': 45},  
        }
    },
    '야전 의료': {
        'name': 'Field Medicine',
        'Type': 'Passive',
        'Description': '''보유 시 HP %를 지속적으로 회복한다''',
        'Buff': {
            1: {'HP_Regen%': 3}, 
            2: {'HP_Regen%': 6}, 
            3: {'HP_Regen%': 9},  
        }
    },
    '마력 반환': {
        'name': 'Mana Return',
        'Type': 'Passive',
        'Description': '''보유 시 MP %를 지속적으로 회복한다''',
        'Buff': {
            1: {'MP_Regen%': 3}, 
            2: {'MP_Regen%': 6}, 
            3: {'MP_Regen%': 9},  
        }
    },
    '아마데우스': {
        'name': 'Amadeus',
        'Type': 'Passive',
        'Description': '''보유 시 경험치 획득량 %이 증가한다''',
        'Buff_%': {
            1: {'EXP_multiplier': 10}, 
            2: {'EXP_multiplier': 20}, 
            3: {'EXP_multiplier': 3000},  
        }
    },
    '다시 불타는 혼': {
        'name': 'Burning Soul Again',
        'Type': 'Passive_Conditional',
        'Description': '''보유 시 레벨업 시 HP,MP %를 추가로 회복한다''',
        'Buff_%': {
            1: {'Level_Up_Regen': 10}, 
            2: {'Level_Up_Regen': 20}, 
            3: {'Level_Up_Regen': 30},  
        }
    },
    '무념의 기보': {
        'Type': 'Passive_Conditional',
        'Description': '''보유 시 {Turn_Without_Magic} 턴 동안 마법을 사용하지 않을 시 Mov가 1 상승한다.''',
        'Judge_Type': ['equal', 'more'],
        'Condition': {
            1: {'Turn_Without_Magic': 4},
            2: {'Turn_Without_Magic': 3},
            3: {'Turn_Without_Magic': 2}
        },
        'Buff': {
            1: {'Mov': 1},
            2: {'Mov': 1},
            3: {'Mov': 1}
        },
    },
    '불굴의 의지': {
        'name': 'Indomitable Will',
        'Type': 'Passive',
        'Description': '''보유 시 HP가 {Condition}% 이하이면 STR이 증가한다. ''',
        'Condition': {
            'type' : ['equal','more'],
            1: {'Max_HP': 50}, 
            2: {'Max_HP': 50}, 
            3: {'Max_HP': 50}, 
        },
        'Buff': {
            1: {'STR': 10}, 
            2: {'STR': 15}, 
            3: {'STR': 20}, 
        }
    },
    # --- 버프 --- #
    '테스트스킬3': {
        'name': 'Test Skill 3',
        'Type': 'Active',
        'style': 'default',
        'Description' : '''사용 시, 다음 자신 페이즈까지 RES%를 올린다''',
        'skill_type' : 'buff',
        'target' : ['Self'],
        'casting': 'MAGIC_CIRCLE',
        'animate_type'  : 'default',
        'animate'   : 'AURA',
        'duration'  : 1,
        'Buff_%': {
            1: {'RES': 20},
            2: {'RES': 40},
            3: {'RES': 60},
        },
    },
    '근접 방어 태세': {
        'name': 'Melee Defense Stance',
        'Type': 'Active',
        'style': 'default',
        'Description' : '''사용 시, 다음 자신 페이즈까지 받는 근접 피해량%을 줄인다''',
        'skill_type' : 'buff',
        'target' : ['Self'],
        'casting': 'MAGIC_CIRCLE',
        'animate_type'  : 'default',
        'animate'   : 'AURA',
        'duration'  : 1,
        'Buff_%': {
            1: {'Melee_defense_multiplier' : -40},
            2: {'Melee_defense_multiplier' : -60},
            3: {'Melee_defense_multiplier' : -70},
        },
    },
    # --- 액티브 --- #
    '아이스': {
        'name': 'Ice',
        'Type': 'Active',
        'style': 'magic',
        'Description' : '''{Range}칸 내 한 명에게 얼음 공격을 가한다''',
        'skill_type': 'Targeting',
        'target' : ['Enemy','Ally'],
        'shape' : 'diamond',
        'target' : 'Self_Enemy',
        'animate_type' : 'default',
        'animate'   : 'ICE1',
        'casting': 'MAGIC_CIRCLE',
        'Dmg_timing' : 1000,
        'Dmg_Coff': {
            1: 35,
            2: 45,
            3: 60
        },
        'Mana': {
            1: 20,
            2: 25,
            3: 30,
        },
        'Range': {
            1 : 5,
            2 : 6,
            3 : 7,
        },
        'Status_%' : {
            1: {'동결' : 100,'약화' : 100},    # 데미지 입을 시 10% 확률로 동결 상태이상
            2: {'동결' : 100,'약화' : 100},    
            3: {'동결' : 100, '약화' : 10},    
        }
    },
    '테스트스킬1': {
        'name': 'Test Skill 1',
        'Type': 'Active',
        'style': 'magic',
        'Description' : '''전방 {Range}칸 내의 모두에게 얼음 공격을 가한다''',
        'skill_type': 'Targeting_all',
        'shape' : 'linear',
        'target' : ['Self_Enemy','Self_Ally'],
        'animate_type' : 'all_tiles',
        'animate'   : 'ICE1',
        'casting': 'MAGIC_CIRCLE',
        'Dmg_timing' : 1000,
        'Dmg_Coff': {
            1: 35,
            2: 45,
            3: 60
        },
        'Mana': {
            1: 20,
            2: 25,
            3: 30,
        },
        'Range': {
            1 : 5,
            2 : 6,
            3 : 7,
        },
        'Status_%' : {
            1: {'동결' : 10},    # 데미지 입을 시 10% 확률로 동결 상태이상
            2: {'동결' : 15},    
            3: {'동결' : 20, '약화' : 10},    
        },
    },
    '테스트스킬2': {
        'name': 'Test Skill 2',
        'Type': 'Active',
        'style': 'magic',
        'Description' : '''{Range}칸 내 자신을 제외한 모두에게 번개를 소환한다''',
        'skill_type': 'Targeting_all',
        'shape' : 'diamond',
        'target' : ['Self_Enemy','Self_Ally_except_Self'],
        'casting': 'MAGIC_CIRCLE',
        'animate_type' : 'default',
        'animate'   : 'THUNDER1',
        'Dmg_timing' : 400,
        'Dmg_Coff': {
            1: 40,
            2: 50,
            3: 60,
        },
        'Mana': {
            1: 20,
            2: 25,
            3: 30,
            },
        'Range': {
            1 : 3,
            2 : 4,
            3 : 5,
        },
        'Status_%' : {
            1: {'약화' : 50},    # 데미지 입을 시 10% 확률로 동결 상태이상
            2: {'약화' : 55},    
            3: {'약화' : 60},   
        },
    },
    '테스트스킬5': {
        'name': 'Test Skill 5',
        'Type': 'Active',
        'style': 'magic',
        'Description': '''전방 {Range}칸 내의 모두에게 불 공격을 한다.''',
        'skill_type': 'Targeting_all',
        'shape': 'linear',
        'target': ['Self_Enemy', 'Self_Ally'],
        'animate_type': 'sequentially',
        'animate': 'FIRE1',
        'casting': 'MAGIC_CIRCLE',
        'sequence_delay': 0.15,  # 각 타일 간 딜레이(초)
        'Dmg_timing': 0.4,  # 애니메이션과 동시에 데미지
        'Dmg_Coff': {
            1: 35,
            2: 45,
            3: 60
        },
        'Mana': {
            1: 20,
            2: 25,
            3: 30,
        },
        'Range': {
            1: 5,
            2: 6,
            3: 7,
        },
        'Status_%': {
            1: {'약화': 20},
            2: {'약화': 25},
            3: {'약화': 30},
        },
    },
    # --- 특수스킬 --- #
    '군의학': {
        'name': 'Military Medicine',
        'Type': 'Active',
        'style': 'yellow',
        'Description': '''의술을 사용하여 아군 한 명의 체력을 크게 회복시킨다.''',
        'skill_type': 'Targeting',  # 단일 타겟팅
        'shape' : 'diamond',
        'target': ['Self_Ally'],  # 자신을 포함한 모든 아군 지정 가능
        'casting': 'MAGIC_CIRCLE',
        'animate': 'HEAL',
        'Dmg_timing': 500,
        'Value': {  # 회복량
            1: {'Cur_HP': 25},
            2: {'Cur_HP': 40},
            3: {'Cur_HP': 60}
        },
        'Mana': {  # 마나 소모량
            1: 20,
            2: 25,
            3: 30,
        },
        'Range': {  # 범위
            1: 2,
            2: 3,
            3: 3
        }
    }
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
        'duration': 1,  # 지속 턴 수
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
        'Effect': {
            'Heal_%': {'Cur_HP': 30}  # 퍼센트 기반 회복
        }
    },
    'MP_Potion': {
        'name': 'MP 포션',
        'Description': '''MP를 50 회복시킨다''',
        'Type': 'Active',
        'animate': 'AURA',
        'Effect': {
            'Heal': {'Cur_MP': 50}  # 고정값 회복
        }
    },
    'Shield_Potion': {
        'name': '방어력 포션',
        'Description': '''3턴간 방어력이 10 상승한다''',
        'Type': 'Buff',
        'animate': 'POTION',
        'Effect': {
            'Buff': {'RES': 10},
            'duration': 3
        }
    },
    'Battle_Potion': {
        'name': '전투력 포션',
        'Description': '''해당 전투 동안 카리스마가 20 상승한다''',
        'Type': 'Permanent',
        'animate': 'AURA',
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
        'STAT' : {'CHA' : 20, 'Melee_attack_multiplier' : 10, 'Range_attack_multiplier' : 10, 'Magic_attack_multiplier' : 10,},
    },
    '절망' : {
        'Description' : '''CHA가 20 감소하며, 주는 근접,마법,원거리 데미지 피해량이 20% 증가한다.''',
        'STAT' : {'CHA' : -20, 'Melee_attack_multiplier' : 20, 'Range_attack_multiplier' : 20, 'Magic_attack_multiplier' : 20,},
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
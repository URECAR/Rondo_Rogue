# character.py
import pygame
import os
from properties import *
from support import  EffectManager, Effect
from common_method import import_folder
from database import MAP1
from database import CharacterDatabase
from database import SKILL_PROPERTIES, STATUS_PROPERTIES, EQUIP_PROPERTIES
from animation import Animation
class Character(pygame.sprite.Sprite):
    def __init__(self, pos, groups, obstacle_sprites, char_type='None', team='Neutral', ):
        super().__init__(groups)
        self.sprite_type = 'Character'
        # 기본 캐릭터 정보
        self.char_type = char_type
        self.team = team
        self.groups = groups
        self.visible_sprites = self.groups[0]
        self.selected = False
        self.isacting = False
        self.isfollowing_root = False
        self.ismove = False
        self.obstacle_sprites = obstacle_sprites
        self.effect_manager = EffectManager()
        # 위치 및 이동
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.Goto = pygame.math.Vector2()
        self.Goto_graphic = pygame.math.Vector2()
        self.move_per_tile = 8  # 기본 이동 속도
        self.enable_hpbar = True
        self.hp_bar = HPBar(self)
        self.visible_sprites.add(self.hp_bar)
        self.facing = 'down'
        self.priority = self.pos[1] * TILESIZE 
        self.collision_rect = pygame.Rect(0, 0, TILESIZE, TILESIZE)
        self.collision_rect.center = (self.pos + pygame.math.Vector2(0.5, 0.5)) * TILESIZE
        
        # 애니메이션 관련 변수
        self.frame_index = 0

        self.death_animation = None
        self.isdeathing = False
        self.isdead = False
        self.inactive = True
        self.original_image = None
        self.current_graphic = None
        # Act 관련 변수
        self.actlist = []
        self.waiting = False
        self.wait_time = 0
        self.wait_frame = 0
        self.casting = False
        self.isknockback = False
        self.isknockback_move = False


        self.properties = {}
        
        # 캐릭터 데이터 로드
        char_data = CharacterDatabase.data.get(self.char_type, {})
        if not char_data:
            raise ValueError(f"Invalid character type: {self.char_type}")
        animation_speeds = char_data['graphics'].get('animation_speed', {})
        
        # 그래픽 속성 초기화
        self.graphics_folder = char_data['graphics']['graphics_folder']
        self.has_directions = char_data['graphics']['has_directions']
        self.animation_types = char_data['graphics']['animation_types']
        self.move_per_tile = char_data['graphics'].get('move_speed', 8)  # 기본값 8
        self.attack_delay = char_data['graphics'].get('attack_delay', 0)
        self.attack_afterdelay = char_data['graphics'].get('attack_afterdelay', 0)
        self.die_animation = char_data['graphics'].get('die_animation', None)
        self.graphics_size = char_data['graphics'].get('size', 1.0)  # 기본값 1.0
        self.graphics_offset = char_data['graphics'].get('offset', [0, 0]).copy()  # 기본값 [0, 0]
        self.idle_anime_tick = animation_speeds.get('idle', 16)       # 기본값 16
        self.move_anime_tick = animation_speeds.get('move', 16)       # 기본값 16
        self.selected_anime_tick = animation_speeds.get('selected', 12) # 기본값 12
        self.attack_anime_tick = animation_speeds.get('attack', 20)    # 기본값 20
        self.casting_anime_tick = animation_speeds.get('casting', 16)  # 기본값 16
        self.range_anime_tick = animation_speeds.get('range', 16)     # 기본값 16
        # 기본 이미지 로드 및 애니메이션 초기화
        for anim_type in self.animation_types:
            if self.has_directions and anim_type != 'selected':
                for direction in ['up', 'down', 'left', 'right']:
                    path = f'{self.graphics_folder}/{anim_type}/{direction}'
                    if os.path.exists(path):
                        self.properties[f'{anim_type}_{direction}'] = path
            else:
                path = f'{self.graphics_folder}/{anim_type}'
                if os.path.exists(path):
                    self.properties[anim_type] = path
        
        try:
            default_path = f'{self.graphics_folder}/default.png'
            if os.path.exists(default_path):
                original_image = pygame.image.load(default_path).convert_alpha()
                # size 적용
                new_width = int(original_image.get_width() * self.graphics_size)
                new_height = int(original_image.get_height() * self.graphics_size)
                self.image = pygame.transform.scale(original_image, (new_width, new_height))
                # 실제 이미지 높이 계산
                self.content_top = self.get_image_height(self.image)
            else:
                raise FileNotFoundError(f"Default image not found for {self.char_type}")
            self.content_top = self.get_image_height(self.image)

            # 충돌 감지용 rect 초기화
            
            # 그래픽용 rect는 offset 적용
            self.rect = self.image.get_rect()
            self.rect.center = (self.collision_rect.centerx + self.graphics_offset[0],self.collision_rect.centery + self.graphics_offset[1])
        except Exception as e:
            raise RuntimeError(f"Error loading graphics for {self.char_type}: {e}")

        # 스탯 초기화
        self.name = char_data.get('name', self.char_type)
        self.LV = MAP1.spawns[self.char_type]['Level'] if self.char_type in MAP1.spawns else 1
        self.skills = char_data['skills']
        self.stats = CharacterDatabase.calculate_stats(self.char_type, self.LV)
        self.base_stats = self.stats.copy()
        self.max_items = 4
        self.inventory = char_data.get('inventory', []).copy()
        self.effects = []

        # 장비 효과 적용
        self.equips = char_data.get('equips', []).copy()
        self.init_apply_equipment_effects()

        # 패시브 스킬 효과 적용
        self.init_apply_passive_skills()
        print(str(self.name)+"의 초기 effect 목록 " + str(self.effects))
        self.Cur_HP = int(self.stats['Max_HP'])
        self.Cur_MP = int(self.stats['Max_MP'])

        self.exp = 0
        self.tmp_exp_gain = 0
        
        self.force_inactive = False
        self.activate_condition = {
            'Turn': 0,
            'Turn_Without_Magic': 0,
            'Turn_Without_Melee': 0,
            'Turn_Without_Range': 0,
            'Turn_Without_Move': 0,
            'Turn_Without_Skill': 0,
            'Max_Damage': 0,     
            'HP_ratio' : 0,
            'MP_ratio' : 0,
        }

        # 마지막으로 모든 효과 적용하여 스탯 업데이트
        self.effect_manager.update_effects(self)

    def init_apply_passive_skills(self):
        for skill_name, skill_level in self.skills.items():
            skill_info = SKILL_PROPERTIES.get(skill_name)
            
            if not skill_info:
                print(f"{skill_name} 스킬 불러오기 실패")
                continue
                
            if skill_info['Type'] == 'Passive':
                skill_passive_details = skill_info['Passive']
                
                if skill_passive_details['effect_type'] == 'constant':
                    if 'stats_%' in skill_passive_details['effects'] and skill_passive_details['effects']['stats_%']:
                        effect = Effect(
                            effect_type='passive',
                            effects=skill_passive_details['effects']['stats_%'][skill_level],
                            source=f"passive_{skill_name}",
                            is_percent=True
                        )
                        self.effects.append(effect)
                    if 'stats' in skill_passive_details['effects'] and skill_passive_details['effects']['stats']:
                        effect = Effect(
                            effect_type='passive',
                            effects=skill_passive_details['effects']['stats'][skill_level],
                            source=f"passive_{skill_name}"
                        )
                        self.effects.append(effect)
            
                elif skill_passive_details['effect_type'] == 'conditional':
                    condition = skill_passive_details['condition'].copy()
                    condition['threshold'] = condition['threshold'][skill_level]

                    if 'stats_%' in skill_passive_details['effects'] and skill_passive_details['effects']['stats_%']:
                        effect = Effect(
                            effect_type='passive_conditional',
                            effects=skill_passive_details['effects']['stats_%'][skill_level],
                            source=f"passive_conditional_{skill_name}",
                            condition=condition,
                            is_percent=True
                        )
                        self.effects.append(effect)
                    if 'stats' in skill_passive_details['effects'] and skill_passive_details['effects']['stats']:
                        effect = Effect(
                            effect_type='passive_conditional',
                            effects=skill_passive_details['effects']['stats'][skill_level],
                            source=f"passive_conditional_{skill_name}",
                            condition=condition,
                        )
                        self.effects.append(effect)

    def init_apply_equipment_effects(self):
        for equip_name in self.equips:
            if equip_name in EQUIP_PROPERTIES:
                equip_data = EQUIP_PROPERTIES[equip_name]
                effect_data = {
                    'percent': {},
                    'flat': {}
                }
                
                for stat, value in equip_data['STAT'].items():
                    if 'multiplier' in stat.lower():
                        effect_data['percent'][stat] = value
                    else:
                        effect_data['flat'][stat] = value
                        
                if effect_data['percent']:
                    effect = Effect(
                        effect_type='equipment',
                        effects=effect_data['percent'],
                        source=f"equipment_{equip_name}",
                        is_percent=True
                    )
                    self.effects.append(effect)
                    
                if effect_data['flat']:
                    effect = Effect(
                        effect_type='equipment',
                        effects=effect_data['flat'],
                        source=f"equipment_{equip_name}"
                    )
                    self.effects.append(effect)

    def update_facing_direction(self, target_pos):
        """이동 방향에 따라 facing 방향 업데이트"""
        dx, dy = target_pos
        if abs(dx) > abs(dy):
            self.facing = 'right' if dx > 0 else 'left'
        elif abs(dx) < abs(dy):
            self.facing = 'down' if dy > 0 else 'up'

    def act(self):
        if not self.isacting and not self.waiting:
            action = self.actlist[0]

            self.isacting = True

            if action == 'move_down':
                self.moveto(0, TILESIZE)
            elif action == 'move_up':
                self.moveto(0, -TILESIZE)
            elif action == 'move_left':
                self.moveto(-TILESIZE, 0)
            elif action == 'move_right':
                self.moveto(TILESIZE, 0)
            elif action == 'turn_left':
                self.facing = DIRECTIONS[(DIRECTIONS.index(self.facing) + 1) % 4]
                self.update_facing_direction((self.rect.x + TILESIZE, self.rect.y))
                self.actlist.pop(0)
            elif action == 'turn_right':
                self.facing = DIRECTIONS[(DIRECTIONS.index(self.facing) - 1) % 4]
                self.update_facing_direction((self.rect.x + TILESIZE, self.rect.y))
                self.actlist.pop(0)
            elif action.startswith('dynamic_move_'):
                _, _, dx, dy, _ = action.split('_')
                self.Goto_graphic.x = float(dx) * 16
                self.Goto_graphic.y = float(dy) * 16
                self.isknockback_move = True
                self.isacting = True
            elif action == 'SW_ON_isknockback':
                self.isknockback = True
                self.isacting = False
                self.actlist.pop(0)
            elif action == 'SW_OFF_isknockback':
                self.isknockback = False
                self.isacting = False
                self.actlist.pop(0)
            elif action == 'act_for_attack':
                self.waiting = True
                self.isacting = True
                self.isfollowing_root = False
                self.wait_time = pygame.time.get_ticks() + self.attack_delay + self.attack_afterdelay
            elif action == 'range_attack':
                self.waiting = True
                self.isacting = True
                self.wait_time = pygame.time.get_ticks() + self.attack_delay
            elif action == 'casting':
                self.casting = True
                self.waiting = True
                self.wait_time = pygame.time.get_ticks() + 1000
            elif action[:5] == 'wait_':
                self.waiting = True
                self.isacting = True
                self.isfollowing_root = False
                self.wait_time = pygame.time.get_ticks() + int(action[5:])
       
            # else:
            #     print("잘못됨")
            #     self.isacting = False
            #     self.actlist.pop(0)
            #     self.isfollowing_root = True
        elif self.waiting and (self.wait_time < pygame.time.get_ticks()):
            self.waiting = False
            self.isacting = False
            self.wait_time = 0  # None 대신 0으로 설정
            if self.actlist[0] == 'casting':
                self.casting = False
            self.actlist.pop(0)  # 먼저 현재 액션 제거
            # 액션 제거 후 다음 액션이 있을 때만 isfollowing_root 설정
            if not self.ismove and self.actlist and not self.isknockback:
                self.isfollowing_root = True

    def battle_return(self, attacker, move_type='knockback'):
        """전투 관련 이동 (넉백, 회피, 반격)
        move_type: 'knockback', 'evasion', 'counter'"""
        knockback_direction = self.pos - attacker.pos
        if knockback_direction.length() > 0:
            knockback_direction.normalize_ip()
            if move_type == 'range_evasion':
                [knockback_direction.x, knockback_direction.y] = [knockback_direction.y, knockback_direction.x]
            # 이동 타입별 설정
            configs = {
                'knockback': {'distance': 1.0, 'wait': 100},
                'evasion': {'distance': 2.0, 'wait': 300},
                'range_evasion': {'distance': 2.0, 'wait': 300},
                'counter': {'distance': 2.0, 'wait': 400}
            }
            config = configs.get(move_type, configs['knockback'])
            
            self.actlist.append('SW_ON_isknockback')
            self.actlist.append(f'dynamic_move_{config["distance"] * knockback_direction.x}_{config["distance"] * knockback_direction.y}_out')
            self.actlist.append(f'wait_{config["wait"]}')
            self.actlist.append(f'dynamic_move_{-config["distance"] * knockback_direction.x}_{-config["distance"] * knockback_direction.y}_in')
            self.actlist.append('SW_OFF_isknockback')

    def knockback(self):
        if self.isknockback_move:
            current_action = self.actlist[0]
            if current_action.startswith('dynamic_move_'):
                _, _, dx, dy, move_type = current_action.split('_')
                dx, dy = float(dx), float(dy)
                
                # 진행도 계산 (0.0 ~ 1.0)
                total_distance = (dx**2 + dy**2)**0.5
                remaining_distance = (self.Goto_graphic.x**2 + self.Goto_graphic.y**2)**0.5
                progress = 1.0 - (remaining_distance / (total_distance * TILESIZE))
                
                # 속도 계산 (포물선 형태)
                if move_type == 'out':  # 밖으로 나갈 때: 빨라졌다가 느려짐
                    speed_multiplier = 1.0 - (progress - 0.5)**2 * 4  # 0.5에서 최대
                else:  # 안으로 들어올 때: 느렸다가 빨라짐
                    speed_multiplier = (progress - 0.5)**2 * 4  # 0.5에서 최소
                
                current_speed = self.move_per_tile * (0.5 + speed_multiplier)  # 기본 속도의 0.5 ~ 1.5배
                
                # X축 이동
                if self.Goto_graphic.x > 0:
                    move_x = min(current_speed, self.Goto_graphic.x)
                    self.rect.x += move_x
                    self.Goto_graphic.x -= move_x
                elif self.Goto_graphic.x < 0:
                    move_x = max(-current_speed, self.Goto_graphic.x)
                    self.rect.x += move_x
                    self.Goto_graphic.x -= move_x
                
                # Y축 이동
                if self.Goto_graphic.y > 0:
                    move_y = min(current_speed, self.Goto_graphic.y)
                    self.rect.y += move_y
                    self.Goto_graphic.y -= move_y
                elif self.Goto_graphic.y < 0:
                    move_y = max(-current_speed, self.Goto_graphic.y)
                    self.rect.y += move_y
                    self.Goto_graphic.y -= move_y
                
                # offset 업데이트
                self.graphics_offset[0] = self.rect.centerx - self.collision_rect.centerx
                self.graphics_offset[1] = self.rect.centery - self.collision_rect.centery
                
                if self.Goto_graphic.x == 0 and self.Goto_graphic.y == 0:
                    self.isknockback_move = False
                    self.isacting = False
                    if self.actlist:
                        self.actlist.pop(0)

    def moveto(self,dx,dy):
        self.ismove = True
        self.update_facing_direction((dx,dy))
        self.Goto.x += dx
        self.Goto.y += dy

    def move(self):
        """지정된 방향으로 이동"""
        # collision_rect 이동
        if self.Goto.x > 0:
            self.collision_rect.x = min(self.collision_rect.x + self.move_per_tile, self.collision_rect.x + self.Goto.x)
            self.Goto.x -= min(self.move_per_tile, self.Goto.x)
        elif self.Goto.x < 0:
            self.collision_rect.x = max(self.collision_rect.x - self.move_per_tile, self.collision_rect.x + self.Goto.x)
            self.Goto.x += max(self.move_per_tile, self.Goto.x)
            
        if self.Goto.y > 0:
            self.collision_rect.y = min(self.collision_rect.y + self.move_per_tile, self.collision_rect.y + self.Goto.y)
            self.Goto.y -= min(self.move_per_tile, self.Goto.y)
        elif self.Goto.y < 0:
            self.collision_rect.y = max(self.collision_rect.y - self.move_per_tile, self.collision_rect.y + self.Goto.y)
            self.Goto.y += max(self.move_per_tile, self.Goto.y)

        # 그래픽용 rect 업데이트 (offset 적용)
        self.rect.center = (
            self.collision_rect.centerx + self.graphics_offset[0],
            self.collision_rect.centery + self.graphics_offset[1]
        )
        if self.selected:
            self.priority = (self.pos[1] + 1) * TILESIZE
        else:
            self.priority = self.pos[1] * TILESIZE

        if self.Goto.x == 0 and self.Goto.y == 0:
            self.ismove = False
            if self.isfollowing_root:
                self.pos = pygame.math.Vector2(self.return_tile_location()[0] // TILESIZE, self.return_tile_location()[1] // TILESIZE)
                if self.selected:
                    self.priority = (self.pos[1] + 1) * TILESIZE
                else:
                    self.priority = self.pos[1] * TILESIZE
            if self.isacting:
                self.isacting = False
                if not self.waiting:
                    self.actlist.pop(0)
                    if self.ismove and not self.actlist:
                        self.ismove = False

    def get_image_height(self, surface):
            """이미지에서 불투명한 픽셀이 있는 가장 위쪽 y좌표를 찾음"""
            width = surface.get_width()
            height = surface.get_height()
            
            for y in range(height):
                for x in range(width):
                    color = surface.get_at((x, y))
                    if color.a > 0:  # 알파값이 0보다 크면 불투명한 픽셀
                        return y
            return 0

    def death(self):
        """사망 시작"""
        self.isdeathing = True
        # 먼저 캐릭터를 투명하게 만듦
        
        if self.die_animation:
            self.death_animation = Animation(self, self.die_animation)
            self.image = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
            self.visible_sprites.add(self.death_animation)

    def deathing(self):
        if self.isdeathing and not self.death_animation.alive():
            self.visible_sprites.remove(self.death_animation)
            # HP Bar 제거
            if hasattr(self, 'hp_bar') and self.hp_bar:
                self.hp_bar.kill()
                
            # 모든 그룹에서 제거
            for group in self.groups:
                if self in group:
                    group.remove(self)
            
            # obstacle_sprites에서도 제거
            if self in self.obstacle_sprites:
                self.obstacle_sprites.remove(self)
                
            self.isdead = True

    def get_animation_key(self, base_type):
        if base_type == 'selected' or not self.has_directions:
            return base_type
        return f'{base_type}_{self.facing}'
    
    def darken_image(self, surface):
        darkened = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                color = surface.get_at((x, y))
                if color.a > 0:
                    darkened.set_at((x, y), (int(color.r * 0.6), int(color.g * 0.6), int(color.b * 0.6), color.a ))
                else:
                    darkened.set_at((x, y), (0, 0, 0, 0))
        return darkened
    
    def play_animation(self, animation_type):
        anim_key = self.get_animation_key(animation_type)
        # 애니메이션 타입이 바뀌면 frame_index 초기화
        if anim_key != self.current_graphic:
            self.frame_index = 0
        self.current_graphic = anim_key
        
        if anim_key in self.properties:
            animation_frames = import_folder(self.properties[anim_key])
            
            # size 적용
            scaled_frames = []
            for frame in animation_frames:
                new_width = int(frame.get_width() * self.graphics_size)
                new_height = int(frame.get_height() * self.graphics_size)
                scaled_frames.append(pygame.transform.scale(frame, (new_width, new_height)))
            animation_frames = scaled_frames
            
            dark_key = f'dark_{anim_key}'
            if not hasattr(self, 'darkened_frames'):
                self.darkened_frames = {}
            if dark_key not in self.darkened_frames:
                self.darkened_frames[dark_key] = [self.darken_image(frame) for frame in animation_frames]
            
            tick = (self.selected_anime_tick if animation_type == 'selected' 
                    else self.idle_anime_tick if animation_type == 'idle' 
                    else self.attack_anime_tick if animation_type == 'attack'
                    else self.casting_anime_tick if animation_type == 'casting'
                    else self.range_anime_tick if animation_type == 'range'
                    else self.move_anime_tick if animation_type == 'move'
                    else self.idle_anime_tick)  # 기본값은 idle_anime_tick
            
            self.frame_index = (self.frame_index + 1) % (len(animation_frames) * tick)
            if self.inactive:
                self.image = self.darkened_frames[dark_key][self.frame_index // tick]
            else:
                self.image = animation_frames[self.frame_index // tick]
            old_center = self.collision_rect.center
            self.rect = self.image.get_rect()
            self.rect.center = (
                old_center[0] + self.graphics_offset[0],
                old_center[1] + self.graphics_offset[1]
            )

    def update(self):
        # 기존 업데이트 로직
        if self.isdeathing:
            self.deathing()
        elif not self.isdead:
            # force_inactive가 True면 행동 불가

            self.hp_bar.update()
            if self.actlist:   
                self.act()
            if self.ismove: 
                self.move()
            if self.isknockback_move:
                self.play_animation('hit')
                self.knockback()
            if self.isfollowing_root:
                if 'move' in self.animation_types:
                    self.play_animation('move')
            else:
                if self.actlist and self.actlist[0] == 'act_for_attack':
                    self.play_animation('attack')
                elif self.actlist and self.actlist[0] == 'range_attack':
                    self.play_animation('range')
                elif self.casting and 'casting' in self.animation_types: 
                    self.play_animation('casting')
                elif self.selected and 'selected' in self.animation_types:
                    self.play_animation('selected')
                elif 'idle' in self.animation_types:
                    self.play_animation('idle')

            
    def return_tile_location(self):
        """충돌 감지용 rect의 위치 반환"""
        return [self.collision_rect.centerx - 0.5 * TILESIZE, self.collision_rect.centery - 0.5 * TILESIZE]

class HPBar(pygame.sprite.Sprite):
    def __init__(self, parent):
        super().__init__()
        self.sprite_type = 'HPBar'
        self.parent = parent
        self.hp_bar_width = 64
        self.hp_bar_height = 8
        self.border_thickness = 2
        self.shadow_height = 3

        total_width = self.hp_bar_width + self.border_thickness * 2
        total_height = self.hp_bar_height + self.border_thickness * 2
        self.image = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        # HP 바의 priority는 항상 부모 캐릭터보다 높게 설정
        self.priority = 0  # update에서 동적으로 설정됨

    def update(self):
        hp_ratio = self.parent.Cur_HP / self.parent.stats['Max_HP']

        # 1. 외곽 검정 라인 (체력바 전체 크기 + 외곽선)
        self.image.fill((0, 0, 0))

        # 2. 체력바 배경 설정 (회색) - 외곽선 내부에 위치
        background_rect = pygame.Rect(
            self.border_thickness, 
            self.border_thickness, 
            self.hp_bar_width, 
            self.hp_bar_height
        )
        pygame.draw.rect(self.image, (128, 128, 128), background_rect)

        # 3. 체력바 (녹색 또는 빨간색)
        hp_bar_width = max(0, int(self.hp_bar_width * hp_ratio))
        hp_bar_color = (255, 0, 0) if self.parent.team == 'Enemy' else (0, 128, 255)
        hp_bar_rect = pygame.Rect(
            self.border_thickness, 
            self.border_thickness, 
            hp_bar_width, 
            self.hp_bar_height
        )
        pygame.draw.rect(self.image, hp_bar_color, hp_bar_rect)

        # 4. 어두운 그림자 (체력바 아래쪽)
        if hp_bar_width > 0:
            shadow_rect = pygame.Rect(
                self.border_thickness, 
                self.border_thickness + self.hp_bar_height - self.shadow_height, 
                hp_bar_width, 
                self.shadow_height
            )
            shadow_color = (
                hp_bar_color[0] // 1.5, 
                hp_bar_color[1] // 1.5, 
                hp_bar_color[2] // 1.5
            )
            pygame.draw.rect(self.image, shadow_color, shadow_rect)

        # 5. 체력바 위치 설정
        # 불투명한 픽셀이 시작되는 위치 찾기
        

        # offset 고려하여 HP바 위치 조정
        self.rect.centerx = self.parent.collision_rect.centerx + self.parent.graphics_offset[0]
        self.rect.bottom = self.parent.rect.top + self.parent.content_top - 10

        # HP 바의 priority는 항상 부모 캐릭터의 priority보다 약간 높게 설정
        self.priority = self.parent.priority - 1


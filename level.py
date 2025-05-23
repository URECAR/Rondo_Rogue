# level.py
from properties import *
import pygame
from support import *
# from player import Player
from tile import Tile, TreeSprite
from random import choice,randint
from debug import debug
from cursor import Cursor
from ui import UI
from map_act import MapAction
from character import Character
from database import MAP1
from animation import AnimationManager
from common_method import import_csv_layout,combine_range_csvs
import math
class Level:
    def __init__(self):

        # display surface 지정
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = YSortCameraGroup()           # 화면 출력용 sprite
        self.obstacle_sprites = pygame.sprite.Group()       # 이동 불가용 sprite
        self.selectable_sprites = pygame.sprite.Group()     # Cursor Target 여부 sprite (Target 당하기만 해도 player의 status, 오브젝트명 출력. 클릭은 player와 enemy만)
        self.battler_sprites = pygame.sprite.Group()        # 배틀이 가능한 sprite
        self.tree_sprites = pygame.sprite.Group()        # 배틀이 가능한 sprite
        self.animation_manager = AnimationManager(self.visible_sprites,self)
        self.ui = UI(self)
        self.Camera_mode = 'Custom'                         # Character면 플레이어의 기준으로 offset 조정, Custom이면 상관없이 카메라 조정. 추후 추가예정.
        self.Camera_offset = [0,0]                          # Custom_draw의 offset
        self.menu_mode = 'explore'                           # select면 cursor의 이동, player_0이면 플레이어 선택 및 status 출력. player_move_0면 이동 경로, object면 status 출력.
        # self.create_map1()                                  # map1 생성
        self.create_map2()
        self.map_action = MapAction(self)  # MapAction 인스턴스 생성

    def create_map2(self):
            # 맵 데이터 로드
            map_data = {
                'layer1': import_csv_layout('../map2/map2._Layer1.csv'),
                'layer2': import_csv_layout('../map2/map2._Layer2.csv'),
                'layer3': import_csv_layout('../map2/map2._Layer3.csv'),
                'layerAbove': import_csv_layout('../map2/map2._LayerAbove.csv'),
                'tree': import_csv_layout('../map2/map2._Tree.csv'),
                'move_data': import_csv_layout('../map2/map2._Move_Data.csv'),
                'range_data': combine_range_csvs([
                    '../map2/map2._Range_Up.csv',
                    '../map2/map2._Range_UpRight.csv',
                    '../map2/map2._Range_Right.csv',
                    '../map2/map2._Range_RightDown.csv',
                    '../map2/map2._Range_Down.csv',
                    '../map2/map2._Range_DownLeft.csv',
                    '../map2/map2._Range_Left.csv',
                    '../map2/map2._Range_LeftUp.csv',
                ])
            }
            
            # 타일셋 로드
            tileset = pygame.image.load('../map2/tileset.png').convert_alpha()
            tileset_width = tileset.get_width() // TILESIZE
            
            # 타일셋에서 타일 이미지 추출
            tile_images = {}
            for tile_id in range(tileset_width * (tileset.get_height() // TILESIZE)):
                x = (tile_id % tileset_width) * TILESIZE
                y = (tile_id // tileset_width) * TILESIZE
                tile_images[str(tile_id)] = tileset.subsurface((x, y, TILESIZE, TILESIZE))
                
            self.level_data = {
                'Map_Max_x': self.visible_sprites.Mapmax.x,
                'Map_Max_y': self.visible_sprites.Mapmax.y,
                'moves': [['-1' if map_data['move_data'][y][x] == '0' else map_data['move_data'][y][x] 
                        for y in range(len(map_data['move_data']))] 
                        for x in range(len(map_data['move_data'][0]))],
                'ranges': [[map_data['range_data'][y][x]
                        for y in range(len(map_data['range_data']))]
                        for x in range(len(map_data['range_data'][0]))]
            }
            
            # Layer1과 LayerAbove를 위한 Surface 생성
            layer1_surface = pygame.Surface((self.level_data['Map_Max_x'], self.level_data['Map_Max_y']), pygame.SRCALPHA)
            layerAbove_surface = pygame.Surface((self.level_data['Map_Max_x'], self.level_data['Map_Max_y']), pygame.SRCALPHA)
            
            # Layer1 렌더링
            for row_index, row in enumerate(map_data['layer1']):
                for col_index, tile_id in enumerate(row):
                    if tile_id != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        tile_image = tile_images[tile_id]
                        layer1_surface.blit(tile_image, (x, y))

            # LayerAbove 렌더링
            for row_index, row in enumerate(map_data['layerAbove']):
                for col_index, tile_id in enumerate(row):
                    if tile_id != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        tile_image = tile_images[tile_id]
                        layerAbove_surface.blit(tile_image, (x, y))

            # Layer1과 LayerAbove를 단일 스프라이트로 생성
            layer1_sprite = Tile((0, 0), [self.visible_sprites], 'layer1', layer1_surface)
            layer1_sprite.priority = 0  # 최하단 레이어

            layerAbove_sprite = Tile((0, 0), [self.visible_sprites], 'layerAbove', layerAbove_surface)
            layerAbove_sprite.priority = self.level_data['Map_Max_y']  # 최상단 레이어

            # Layer2와 Layer3는 개별 타일로 생성
            for layer_name in ['layer2', 'layer3']:
                for row_index, row in enumerate(map_data[layer_name]):
                    for col_index, tile_id in enumerate(row):
                        if tile_id != '-1':
                            x = col_index * TILESIZE
                            y = row_index * TILESIZE
                            groups = [self.visible_sprites]

                            tile = Tile((x, y), groups, layer_name, tile_images[tile_id], tile_id=int(tile_id))

                            # Layer별 priority 설정
                            if layer_name == 'layer2':
                                tile.priority = y
                            else:  # layer3
                                tile.priority = y + 2 * TILESIZE
                                
            # 나무 레이어 처리
            for row_index, row in enumerate(map_data['tree']):
                for col_index, tile_id in enumerate(row):
                    if tile_id in ['339', '730']:  # 트리의 시작점인 경우만 처리
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        TreeSprite((x, y), [self.visible_sprites, self.tree_sprites], 'tree', tileset, int(tile_id))

            self.panorama_background = PanoramaBackground(self)
            self.visible_sprites.add(self.panorama_background)

            # 기본 배틀러(spawn_order=1) 생성
            self.battlers = []
            self.spawn_battlers(1)
            
            # 첫 번째 아군 배틀러의 위치에 커서 생성
            ally_battlers = [b for b in self.battlers if b.team == 'Ally']
            if ally_battlers:
                first_battler = ally_battlers[0]
                self.cursor = Cursor((first_battler.pos.x, first_battler.pos.y), [self.visible_sprites], self)
        
    def spawn_battlers(self, spawn_order):
        """
        특정 spawn_order를 가진 모든 배틀러를 스폰
        spawn_order: 스폰 순서 (1: 기본 스폰, 2/3/4: 추가 스폰)
        """
        # battlers 리스트가 없으면 초기화
        if not hasattr(self, 'battlers'):
            self.battlers = []

        # 해당 spawn_order를 가진 모든 spawn_id 찾기
        spawn_ids = [
            spawn_id for spawn_id, data in MAP1.spawns.items() 
            if data['spawn_order'] == spawn_order
        ]
        
        # 아군 먼저 스폰하기 위해 정렬
        spawn_ids.sort(key=lambda x: MAP1.spawns[x]['team'] != 'Ally')
        
        # 각 spawn_id에 대해 배틀러 생성
        for spawn_id in spawn_ids:
            spawn_data = MAP1.spawns[spawn_id]
            
            # 팀과 캐릭터 타입 가져오기
            team = spawn_data['team']
            char_type = spawn_data['char_type']
            
            # 스폰 위치 결정
            if team == 'Ally' and 'spawn_pos' not in spawn_data:
                # 아군이고 스폰 위치가 지정되지 않은 경우 ally_spawn_points 사용
                ally_count = len([b for b in self.battlers if b.team == 'Ally'])
                spawn_index = ally_count % len(MAP1.ally_spawn_points)
                spawn_x = MAP1.ally_spawn_points[spawn_index][0]
                spawn_y = MAP1.ally_spawn_points[spawn_index][1]
            else:
                # 적군이거나 스폰 위치가 지정된 경우
                spawn_x = spawn_data['spawn_pos'][0]
                spawn_y = spawn_data['spawn_pos'][1]
            
            # 배틀러 생성
            battler = Character(
                (spawn_x, spawn_y),
                [self.visible_sprites, self.selectable_sprites, self.battler_sprites],
                self.obstacle_sprites,
                char_type=char_type,
                team=team
            )
            
            # 레벨 설정
            battler.LV = spawn_data['level']
            battler.base_team = team
            
            # battlers 리스트에 추가
            self.battlers.append(battler)

    def spawn_battler(self, spawn_id, offset=[0,0], team=None):
        """
        개별 배틀러 생성 함수
        spawn_id: spawns 딕셔너리의 키 값
        offset: 스폰 위치 오프셋 [x, y]
        team: 선택적으로 팀 오버라이드
        """
        # battlers 리스트가 없으면 초기화
        if not hasattr(self, 'battlers'):
            self.battlers = []

        if spawn_id not in MAP1.spawns:
            raise ValueError(f"Unknown spawn ID: {spawn_id}")
            
        spawn_data = MAP1.spawns[spawn_id]
        
        # 팀과 캐릭터 타입 가져오기
        base_team = spawn_data['team']
        char_type = spawn_data['char_type']
        
        # 스폰 위치 결정
        if base_team == 'Ally' and 'spawn_pos' not in spawn_data:
            # 기존 아군 수 계산
            ally_count = len([b for b in self.battlers if b.team == 'Ally'])
            spawn_index = ally_count % len(MAP1.ally_spawn_points)
            spawn_x = MAP1.ally_spawn_points[spawn_index][0] + offset[0]
            spawn_y = MAP1.ally_spawn_points[spawn_index][1] + offset[1]
        else:
            # 적군이거나 스폰 위치가 지정된 경우
            spawn_x = spawn_data['spawn_pos'][0] + offset[0]
            spawn_y = spawn_data['spawn_pos'][1] + offset[1]
        
        # 배틀러 생성
        battler = Character(
            (spawn_x, spawn_y),
            [self.visible_sprites, self.selectable_sprites, self.battler_sprites],
            self.obstacle_sprites,
            char_type=char_type,
            team=team if team else base_team
        )
        
        # 레벨 설정
        battler.LV = spawn_data['level']
        battler.base_team = base_team
        
        # battlers 리스트에 추가
        self.battlers.append(battler)
        
        return battler
    
    def level_update(self):
        self.menu_mode = self.map_action.current_mode  # menu_mode 동기화
        
        # # 4x5Tree 스프라이트의 플레이어 감지 체크
        for tree in self.tree_sprites:
            checked = False  # 한 배틀러라도 트리 영역에 있으면 더 이상 체크할 필요 없음
            for battler in self.battler_sprites:
                if tree.check_player_behind(battler.pos):
                    checked = True
                    break
                    
            # 어떤 배틀러도 트리 영역에 없고, 트리가 투명한 상태라면
            if not checked and tree.transparency_needed:
                tree.check_player_behind(pygame.math.Vector2(-1, -1))  # 불가능한 위치 전달하여 투명
                
    def detect_object(self,standard,bias):      # Level의 특정 좌표에 위치한 sprite를 확인할 수 있음.
        detected_list = []
        for sprite in self.selectable_sprites:
            if [sprite.rect.x,sprite.rect.y] == [standard.rect.x + bias[0] * TILESIZE,standard.rect.y + bias[1] * TILESIZE]:
                detected_list.append(sprite)
        return detected_list

    def run(self):
        self.level_update()
        self.panorama_background.update()  # 먼저 파노라마 업데이트
        self.panorama_background.draw()      # 그 다음 파노라마 그리기
        self.visible_sprites.custom_draw(self.cursor)
        self.visible_sprites.update()
        self.map_action.update()
        self.ui.display()
        # 화면에 고정된 스프라이트(예: PHASE_CHANGE 애니메이션) 그리기:
        # debug(self.battlers[0].effects, y=50)
        # debug([s.priority for s in self.visible_sprites if not 'layer' in s.sprite_type ], y=70)
        # debug([s.sprite_type for s in self.visible_sprites if not 'layer' in s.sprite_type], y=110)
        # # debug()
        # debug(self.cursor.pos, x=150)
        # debug(self.map_action.current_state, x=70)
        # debug([battler.OVD_progress for battler in self.battler_sprites], y=90)


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = WIDTH // 2
        self.half_height = HEIGHT // 2
        self.offset = pygame.math.Vector2(0,0)
        self.camera_speed = 4

        # 줌 관련 변수들
        self.zoom_enabled = False
        self.zoom_scale = 1.0
        self.target_zoom = 1.0
        self.min_zoom = 0.5
        self.max_zoom = 2.0
        self.zoom_speed = 0.1
        self.battle_zoom = 2.0

        # 화면 렌더링을 위한 surface
        self.render_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.zoom_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

        # 기존 초기화 코드
        self.floor_surf = pygame.Surface((MAP1.data["Max_X"], MAP1.data["Max_Y"]))
        self.floor_rect = self.floor_surf.get_rect(topleft = (0,0))
        self.Mapmax = pygame.math.Vector2(self.floor_rect[2],self.floor_rect[3])
        self.target_offset = pygame.math.Vector2(0,0)
        self.is_moving = False
        self.move_speed = 0.15

        # 쉐이크 효과 관련 변수 추가
        self.shake_time = 0
        self.shake_duration = 0
        self.shake_intensity = 0
        self.shake_direction = 'horizontal'  # 'horizontal' or 'vertical'
        self.shake_offset = pygame.math.Vector2(0, 0)
        self.last_shake_update = pygame.time.get_ticks()

    def enable_zoom(self):
        """Enable zoom and set target zoom to battle zoom level"""
        self.zoom_enabled = True
        self.target_zoom = self.battle_zoom
        
    def disable_zoom(self):
        """Disable zoom and reset zoom scale to 1.0"""
        self.zoom_enabled = False  # 줌을 끄도록 수정
        self.target_zoom = 1.0
        self.zoom_scale = 1.0

    def zoom_to_battler(self, battler):
        """특정 배틀러에게 줌인"""
        if self.zoom_enabled:
            self.target_zoom = self.battle_zoom
            # 화면 중앙에 배틀러가 오도록 계산
            target_x = battler.collision_rect.centerx - (WIDTH / self.target_zoom)
            target_y = battler.collision_rect.centery - (HEIGHT / self.target_zoom)
            self.target_offset = pygame.math.Vector2(target_x, target_y)
            self.is_moving = True

    def start_shake(self, duration, intensity=5, direction='horizontal'):
        """
        화면 흔들기 효과 시작
        :param duration: 지속 시간 (초)
        :param intensity: 흔들림 강도 (픽셀)
        :param direction: 흔들림 방향 ('horizontal' 또는 'vertical')
        """
        self.shake_time = 0
        self.shake_duration = duration
        self.shake_intensity = intensity
        self.shake_direction = direction
        self.last_shake_update = pygame.time.get_ticks()

    def update_shake(self):
        """쉐이크 효과 업데이트"""
        if self.shake_time < self.shake_duration:
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_shake_update) / 1000.0  # 초 단위로 변환
            self.last_shake_update = current_time
            
            self.shake_time += dt
            
            # 시간에 따른 강도 감소 (서서히 약해지는 효과)
            current_intensity = self.shake_intensity * (1 - (self.shake_time / self.shake_duration))
            
            # 사인 함수를 사용하여 부드러운 흔들림 효과 생성
            shake_amount = math.sin(self.shake_time * 30) * current_intensity
            
            if self.shake_direction == 'horizontal':
                self.shake_offset.x = shake_amount
                self.shake_offset.y = 0
            elif self.shake_direction == 'vertical':
                self.shake_offset.x = 0
                self.shake_offset.y = shake_amount
            else:  # both
                self.shake_offset.x = shake_amount
                self.shake_offset.y = shake_amount
        else:
            # 쉐이크 효과 종료
            self.shake_offset = pygame.math.Vector2(0, 0)

    def custom_draw(self, player):
        # 1. 쉐이크 효과 업데이트
        self.update_shake()
        
        # 2. 카메라 이동 처리
        if self.is_moving:
            diff_x = self.target_offset.x - self.offset.x
            diff_y = self.target_offset.y - self.offset.y
            self.offset.x += diff_x * self.move_speed
            self.offset.y += diff_y * self.move_speed

            if abs(diff_x) < 0.5 and abs(diff_y) < 0.5:
                self.offset = self.target_offset.copy()
                self.is_moving = False
        else:
            target_x = player.rect.centerx - self.half_width
            target_y = player.rect.centery - self.half_height

            if self.offset.x < target_x - CAMERA_MARGIN_X:
                self.offset.x = target_x - CAMERA_MARGIN_X
            elif self.offset.x > target_x + CAMERA_MARGIN_X:
                self.offset.x = target_x + CAMERA_MARGIN_X

            if self.offset.y < target_y - CAMERA_MARGIN_Y:
                self.offset.y = target_y - CAMERA_MARGIN_Y
            elif self.offset.y > target_y + CAMERA_MARGIN_Y:
                self.offset.y = target_y + CAMERA_MARGIN_Y

        # 3. 맵 경계 처리
        self.offset.x = max(0, min(self.offset.x, self.Mapmax.x - WIDTH))
        self.offset.y = max(0, min(self.offset.y, self.Mapmax.y - HEIGHT))
        
        # 4. 쉐이크 오프셋 적용
        final_offset = self.offset + self.shake_offset

        # 5. render_surface에 모든 스프라이트 그리기
        # render_surface를 먼저 클리어합니다.
        self.render_surface.fill((0, 0, 0, 0))
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.priority if hasattr(sprite, 'priority') else sprite.rect.centery):
            # 'Screen_Sprite' 타입은 화면 고정 좌표로 처리합니다.
            if getattr(sprite, "sprite_type", None) == 'Screen_Sprite':
                offset_pos = sprite.rect.topleft
            else:
                offset_pos = sprite.rect.topleft - final_offset
            self.render_surface.blit(sprite.image, offset_pos)
        
        # 6. 줌 처리: zoom_enabled가 True이면 render_surface를 스케일해서 display_surface에 blit
        if self.zoom_enabled:
            # zoom_scale이 target_zoom에 천천히 수렴하도록 업데이트
            if abs(self.zoom_scale - self.target_zoom) > 0.001:
                self.zoom_scale += (self.target_zoom - self.zoom_scale) * self.zoom_speed

            zoom_width = int(WIDTH * self.zoom_scale)
            zoom_height = int(HEIGHT * self.zoom_scale)
            
            # 화면 중앙을 기준으로 scaling
            center_x = WIDTH // 2
            center_y = HEIGHT // 2
            scaled_surface = pygame.transform.scale(self.render_surface, (zoom_width, zoom_height))
            
            # display_surface를 클리어한 후 스케일된 surface를 중앙에 blit
            self.display_surface.fill((0, 0, 0))
            self.display_surface.blit(scaled_surface, (center_x - zoom_width // 2, center_y - zoom_height // 2))
        else:
            # 줌이 꺼져 있으면 render_surface를 그대로 display_surface에 blit
            self.display_surface.blit(self.render_surface, (0, 0))

    def focus_on_target(self, target, cursor_obj=None):
        """특정 대상의 위치로 카메라(부드럽게)와 커서(즉시)를 이동"""
        if not target: return

        # --- 카메라 포커스 (부드러운 이동 유지) ---
        target_cam_x = target.collision_rect.centerx - self.half_width
        target_cam_y = target.collision_rect.centery - self.half_height

        current_view_width = WIDTH / self.zoom_scale if self.zoom_enabled else WIDTH
        current_view_height = HEIGHT / self.zoom_scale if self.zoom_enabled else HEIGHT
        target_cam_x = max(0, min(target_cam_x, self.Mapmax.x - current_view_width))
        target_cam_y = max(0, min(target_cam_y, self.Mapmax.y - current_view_height))

        self.target_offset = pygame.math.Vector2(target_cam_x, target_cam_y)
        self.is_moving = True # 부드러운 카메라 이동 트리거

        # --- 커서 포커스 (즉시 이동) ---
        if cursor_obj:
            # 목표 타일의 좌상단 픽셀 좌표 계산
            target_tile_x = target.pos.x
            target_tile_y = target.pos.y
            target_cursor_pixel_x = target_tile_x * TILESIZE
            target_cursor_pixel_y = target_tile_y * TILESIZE

            # 진행 중인 모든 커서 이동 취소
            cursor_obj.Goto = pygame.math.Vector2(0, 0)
            cursor_obj.ismoving = False
            cursor_obj.is_click_moving = False # 시간 기반 이동도 취소

            # 커서 위치 즉시 설정
            cursor_obj.rect.topleft = (target_cursor_pixel_x, target_cursor_pixel_y)
            cursor_obj.collision_rect.topleft = cursor_obj.rect.topleft

            # 논리적 위치 및 이전 위치 즉시 업데이트
            new_pos = pygame.math.Vector2(target_tile_x, target_tile_y)
            # 위치가 실제로 변경되었는지 확인 (불필요한 사운드 방지)
            # if new_pos != cursor_obj.pos and not cursor_obj.move_lock:
            #     cursor_obj.sound_manager.play_sound(**SOUND_PROPERTIES['CURSOR_MOVE'])
            # focus_on_target 시에는 소리를 내지 않는 것이 자연스러울 수 있습니다. 필요하면 위 주석 해제.
            cursor_obj.pos = new_pos
            cursor_obj.previous_pos = cursor_obj.pos.copy()

            # start_timed_move 호출 제거
            # cursor_obj.start_timed_move(target_pixel_pos) # REMOVED


class PanoramaBackground(pygame.sprite.Sprite):
    def __init__(self, level):
        super().__init__()
        self.sprite_type = 'Panorama'
        self.level = level
        self.display_surface = pygame.display.get_surface()
        
        # 원본 이미지 로드 및 크기 조정
        self.original_image = pygame.image.load("../map2/panorama.jpg").convert_alpha()
        self.original_image = pygame.transform.scale(self.original_image, 
            (self.level.visible_sprites.Mapmax.x * 2, self.level.visible_sprites.Mapmax.y * 2))
        
        # 타일링을 위한 2x2 그리드 생성
        self.panorama_img = pygame.Surface((self.original_image.get_width() * 2, self.original_image.get_height() * 2),pygame.SRCALPHA)
        
        # 4개의 타일 배치
        for x in range(2):
            for y in range(2):
                self.panorama_img.blit(self.original_image, (x * self.original_image.get_width(), y * self.original_image.get_height()))
        
        self.image = self.panorama_img
        self.rect = self.image.get_rect(topleft=(0, 0))
        self.img_x = 0
        self.img_y = 0
        self.move_speed = 0.5
        self.transparency = 120  # 초기 투명도 (0-255)
        self.priority = float('inf')  # 항상 가장 뒤에 그려지도록
        
        # 초기 투명도 설정
        self.update_transparency()
    
    def update_transparency(self):
        """투명도 업데이트"""
        self.image = self.panorama_img.copy()
        self.image.set_alpha(self.transparency)
    
    def update(self):
        # 위치 업데이트
        self.img_x -= self.move_speed
        self.img_y -= self.move_speed
        
        # 무한 스크롤을 위한 위치 재설정
        if self.img_x <= -self.original_image.get_width():
            self.img_x = 0
        if self.img_y <= -self.original_image.get_height():
            self.img_y = 0
            
        self.rect.topleft = (self.img_x, self.img_y)
        
        # 현재 카메라 오프셋에 따라 위치 조정
        self.rect.x = self.img_x - self.level.visible_sprites.offset.x
        self.rect.y = self.img_y - self.level.visible_sprites.offset.y
    
    def draw(self):
        # 현재 화면에 보이는 영역만 그리기
        visible_rect = pygame.Rect(
            self.level.visible_sprites.offset.x,
            self.level.visible_sprites.offset.y,
            self.display_surface.get_width(),
            self.display_surface.get_height()
        )
        
        self.display_surface.blit(
            self.image.subsurface(visible_rect), 
            (0, 0)
        )
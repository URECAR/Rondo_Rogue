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
            'move_data': import_csv_layout('../map2/map2._Move_Data.csv')
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

        # moves 데이터 처리
        moves_data = map_data['move_data']
        self.level_data = {
            'Map_Max_x': self.visible_sprites.Mapmax.x,
            'Map_Max_y': self.visible_sprites.Mapmax.y,
            'moves': [['-1' if map_data['move_data'][y][x] == '0' else map_data['move_data'][y][x] 
                    for y in range(len(map_data['move_data']))] 
                    for x in range(len(map_data['move_data'][0]))]
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
        layer1_sprite = Tile((0, 0),[self.visible_sprites],'layer1',layer1_surface)
        layer1_sprite.priority = 0  # 최하단 레이어

        layerAbove_sprite = Tile((0, 0),[self.visible_sprites],'layerAbove',layerAbove_surface)
        layerAbove_sprite.priority = self.level_data['Map_Max_y']  # 최상단 레이어

        # Layer2와 Layer3는 개별 타일로 생성
        for layer_name in ['layer2', 'layer3']:
            for row_index, row in enumerate(map_data[layer_name]):
                for col_index, tile_id in enumerate(row):
                    if tile_id != '-1':
                        x = col_index * TILESIZE
                        y = row_index * TILESIZE
                        groups = [self.visible_sprites]

                        tile = Tile((x, y),groups,layer_name,tile_images[tile_id],tile_id=int(tile_id))

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

        # 배틀러 생성
        self.battlers = {}
        spawn_order = list(MAP1.spawns.keys())
        
        for char_type in spawn_order:
            self.battlers[char_type] = self.spawn_battler(char_type)
        
        # self.battlers['Piglin2'] = self.spawn_battler('Piglin', offset=[0,1])
        
        # 커서는 첫 배틀러 위치에 생성
        first_battler = self.battlers[spawn_order[0]]
        self.cursor = Cursor((first_battler.pos.x, first_battler.pos.y),[self.visible_sprites],self)
        
    def spawn_battler(self, char_type, offset=[0,0], team=None):
        """배틀러 생성 함수"""
        if char_type not in MAP1.spawns:
            raise ValueError(f"Unknown character type: {char_type}")
            
        spawn_data = MAP1.spawns[char_type]
        spawn_x = spawn_data['Spawn'][0] + offset[0]
        spawn_y = spawn_data['Spawn'][1] + offset[1]
        
        # team이 지정되지 않으면 base_team 사용
        battler_team = team if team else spawn_data['base_team']
        
        battler = Character(
            (spawn_x, spawn_y),
            [self.visible_sprites, self.selectable_sprites, self.battler_sprites],
            self.obstacle_sprites,
            char_type=char_type,
            team=battler_team
        )
        battler.base_team = spawn_data['base_team']
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
        self.panorama_background.draw()    # 그 다음 파노라마 그리기
        self.visible_sprites.custom_draw(self.cursor)
        self.visible_sprites.update()
        self.map_action.update()
        self.ui.display()
        # debug(self.battlers['Player1'].pos)
        debug(self.cursor.pos)
        debug(self.map_action.current_state, x = 70)
        debug(self.map_action.cur_moves, y= 50)
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

    def toggle_zoom(self):
        """줌 활성화/비활성화 토글"""
        self.zoom_enabled = not self.zoom_enabled
        if not self.zoom_enabled:
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

    def custom_draw(self, player):
        # 카메라 이동 처리
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

        # 맵 경계 처리
        self.offset.x = max(0, min(self.offset.x, self.Mapmax.x - WIDTH))
        self.offset.y = max(0, min(self.offset.y, self.Mapmax.y - HEIGHT))
        # 일반 렌더링
        self.render_surface.fill((0, 0, 0, 0))
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.priority if hasattr(sprite, 'priority') else sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.render_surface.blit(sprite.image, offset_pos)

        # 줌 처리
        if self.zoom_enabled:
            if abs(self.zoom_scale - self.target_zoom) > 0.001:
                self.zoom_scale += (self.target_zoom - self.zoom_scale) * self.zoom_speed

            # 줌된 이미지의 크기 계산
            zoom_width = int(WIDTH * self.zoom_scale)
            zoom_height = int(HEIGHT * self.zoom_scale)
            
            # 줌 중심점 계산
            center_x = WIDTH // 2
            center_y = HEIGHT // 2
            
            # 줌된 영역 계산
            zoom_rect = pygame.Rect(center_x - (zoom_width // 2),center_y - (zoom_height // 2),zoom_width,zoom_height)

            # 원본 surface를 줌 크기로 스케일링
            scaled_surface = pygame.transform.scale(self.render_surface,(zoom_width, zoom_height))

            # 줌된 이미지를 화면 중앙에 그리기
            self.display_surface.fill((0, 0, 0))
            self.display_surface.blit(scaled_surface, (center_x - zoom_width // 2,center_y - zoom_height // 2))
        else:
            # 줌이 비활성화된 경우 일반 렌더링
            self.display_surface.blit(self.render_surface, (0, 0))

    def focus_on_target(self, target, cursor_obj=None):
        """특정 대상의 위치로 카메라를 부드럽게 이동, 커서는 즉시 이동"""
        # 타겟의 중앙 위치 계산
        target_x = target.collision_rect.centerx - self.half_width
        target_y = target.collision_rect.centery - self.half_height
        
        # 맵 경계 체크
        target_x = max(0, min(target_x, self.Mapmax.x - WIDTH))
        target_y = max(0, min(target_y, self.Mapmax.y - HEIGHT))

        # 목표 위치 설정
        self.target_offset = pygame.math.Vector2(target_x, target_y)
        self.is_moving = True

        # 커서 즉시 이동
        if cursor_obj:
            cursor_obj.rect.center = target.collision_rect.center
            cursor_obj.Goto = pygame.math.Vector2(0, 0)  # 이동 중인 상태 초기화
            cursor_obj.pos = pygame.math.Vector2(cursor_obj.rect.topleft[0] // TILESIZE, cursor_obj.rect.topleft[1] // TILESIZE)

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
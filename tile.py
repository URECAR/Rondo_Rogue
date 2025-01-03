import pygame 
from properties import *

####
# Sprite Tile will be '1x2 Object, 2x2 Object, 4x5 Tree, 2x1 Statue, etc...

class Tile(pygame.sprite.Sprite):
    def __init__(self, pos, groups, sprite_type, surface=pygame.Surface((TILESIZE, TILESIZE)), path_info=None, tile_id = None):
        super().__init__(groups)
        self.type = 'Tile'
        self.pos = pygame.math.Vector2(pos[0] // TILESIZE, pos[1] // TILESIZE)
        self.sprite_type = sprite_type
        self.selected = False
        self.original_image = None
        self.transparency_needed = False
        self.tile_id = tile_id
        if sprite_type == 'area_display_tile':
            self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            self.rect = self.image.get_rect(topleft=pos)
            self.pos = pygame.math.Vector2(self.rect.topleft[0] // TILESIZE, self.rect.topleft[1] // TILESIZE)
            self.priority = self.rect.topleft[1] + 1  # 가장 아래에 그려지도록
            self.hitbox = self.rect
            
        elif sprite_type == 'tree':
            self.image = surface
            self.original_image = surface.copy()
            self.rect = self.image.get_rect(topleft=pos)
            self.pos = pygame.math.Vector2(self.rect.topleft[0] // TILESIZE, self.rect.topleft[1] // TILESIZE)
            if 698 <= self.tile_id <= 733:
                self.priority = (733 - self.tile_id) // 8 * TILESIZE + self.rect.topleft[1]
            elif 315 <= self.tile_id <= 341:
                self.priority = (341 - self.tile_id) // 8 * TILESIZE + self.rect.topleft[1]
                
        elif sprite_type == 'move_root':
            self.rect = pygame.Rect(pos[0], pos[1], TILESIZE, TILESIZE)
            self.priority = self.rect.topleft[1] + 1
            if path_info:
                prev_dir, next_dir = path_info
                
                # 다음 타일이 없는 경우 (끝 타일)
                if not next_dir:
                    image = pygame.image.load('../graphics/UI/linear_end.png').convert_alpha()
                    rotation = {
                        'up': 90,
                        'right': 0,
                        'down': -90,
                        'left': 180
                    }.get(prev_dir, 0)
                    self.image = pygame.transform.rotate(image, rotation)
                
                # 직선인 경우
                elif prev_dir == next_dir:
                    image = pygame.image.load('../graphics/UI/linear.png').convert_alpha()
                    self.image = pygame.transform.rotate(image, 90 if prev_dir in ['up', 'down'] else 0)
                
                # 커브인 경우
                else:
                    image = pygame.image.load('../graphics/UI/curve.png').convert_alpha()
                    # 회전 각도 결정
                    rotation = 0
                    if (prev_dir == 'right' and next_dir == 'up') or (prev_dir == 'down' and next_dir == 'left'):
                        rotation = 0
                    elif (prev_dir == 'up' and next_dir == 'left') or (prev_dir == 'right' and next_dir == 'down'):
                        rotation = 90
                    elif (prev_dir == 'left' and next_dir == 'down') or (prev_dir == 'up' and next_dir == 'right'):
                        rotation = 180
                    elif (prev_dir == 'down' and next_dir == 'right') or (prev_dir == 'left' and next_dir == 'up'):
                        rotation = -90
                    self.image = pygame.transform.rotate(image, rotation)
            else:
                image = pygame.image.load('../graphics/UI/linear.png').convert_alpha()
                self.image = image

            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect
            self.priority = self.rect.topleft[1]


        else:  # 기타 타일
            self.image = surface
            self.rect = self.image.get_rect(topleft=pos)
            self.hitbox = self.rect
            self.priority = self.rect.topleft[1]  # 기존 priority 계산 유지

    def check_player_behind(self, player_pos):
        """플레이어가 트리 영역 안에 있는지 확인"""
        # 트리의 영역 내에 있는지 확인
        tree_area_x = range(int(self.pos.x), int(self.pos.x + self.size[0]))
        tree_area_y = range(int(self.pos.y - self.size[1] + 1), int(self.pos.y + 1))
        
        if player_pos.x in tree_area_x and player_pos.y in tree_area_y:
            if not self.transparency_needed:
                self.transparency_needed = True
                self.image = self.original_image.copy()
                self.image.set_alpha(127)
            return True
        elif self.transparency_needed:
            self.transparency_needed = False
            self.image = self.original_image.copy()
            self.image.set_alpha(255)
        return False

    @classmethod
    def update_path_tiles(cls, move_roots, visible_sprites, obstacle_sprites, selected_battler):
        """이동 경로의 타일들을 업데이트"""
        from common_method import determine_direction
        
        for i in range(len(move_roots)):
            current_tile = move_roots[i][0]
            current_pos = current_tile.rect.topleft
            
            # 마지막 타일은 화살표
            if i == len(move_roots) - 1:
                prev_pos = move_roots[i-1][0].rect.topleft if i > 0 else [selected_battler.collision_rect.centerx - 0.5 * TILESIZE,selected_battler.collision_rect.centery - 0.5 * TILESIZE]
                direction = determine_direction(prev_pos, current_pos)
                current_tile.kill()
                new_tile = cls(
                    current_pos,
                    [visible_sprites, obstacle_sprites],
                    'move_root',
                    path_info=(direction, None)
                )
                move_roots[i][0] = new_tile
            # 중간 타일
            else:
                prev_pos = move_roots[i-1][0].rect.topleft if i > 0 else [selected_battler.collision_rect.centerx - 0.5 * TILESIZE,selected_battler.collision_rect.centery - 0.5 * TILESIZE]
                next_pos = move_roots[i+1][0].rect.topleft
                prev_dir = determine_direction(prev_pos, current_pos)
                next_dir = determine_direction(current_pos, next_pos)
                current_tile.kill()
                new_tile = cls(
                    current_pos,
                    [visible_sprites, obstacle_sprites],
                    'move_root',
                    path_info=(prev_dir, next_dir)
                )
                move_roots[i][0] = new_tile

class TreeSprite(pygame.sprite.Sprite):
    def __init__(self, pos, groups, tree_type, tileset, base_tile_id):
        super().__init__(groups)
        self.sprite_type = 'tree'
        self.pos = pygame.math.Vector2(pos[0] // TILESIZE, pos[1] // TILESIZE)
        self.transparency_needed = False

        # 트리 타입에 따른 크기 설정
        if base_tile_id == 339:  # 3x4 트리
            self.size = (3, 4)  # (가로, 세로)
            # 아래에서 위로 올라가면서, 왼쪽에서 오른쪽으로 타일 범위 생성
            tile_range = [(x, y) for y in range(3, -1, -1) for x in range(3)]
        elif base_tile_id == 730:  # 4x5 트리
            self.size = (4, 5)  # (가로, 세로)
            tile_range = [(x, y) for y in range(4, -1, -1) for x in range(4)]

        self.image = pygame.Surface((self.size[0] * TILESIZE, self.size[1] * TILESIZE), pygame.SRCALPHA)
        tileset_width = tileset.get_width() // TILESIZE
        
        # 타일 조합 시 y좌표 반전
        for x, y in tile_range:
            current_id = base_tile_id + x - (y * 8)  # y 방향으로 올라갈 때마다 8씩 빼기
            tile_x = (current_id % tileset_width) * TILESIZE
            tile_y = (current_id // tileset_width) * TILESIZE
            tile_image = tileset.subsurface((tile_x, tile_y, TILESIZE, TILESIZE))
            # 실제 이미지에 그릴 때는 위에서부터 그리도록 y좌표 조정
            self.image.blit(tile_image, (x * TILESIZE, (self.size[1] - y - 1) * TILESIZE))

        self.original_image = self.image.copy()
        self.rect = self.image.get_rect(bottomleft=(pos[0], pos[1] + TILESIZE))
        self.priority = pos[1]

    def check_player_behind(self, player_pos):
        """플레이어가 트리 영역 안에 있는지 확인"""
        tree_x = self.pos.x
        tree_y = self.pos.y
        
        # Tree의 전체 영역 체크 (pos는 트리의 왼쪽 아래 기준)
        if (tree_x <= player_pos.x < tree_x + self.size[0] and  # x 범위 체크
            tree_y - self.size[1] < player_pos.y <= tree_y):    # y 범위 체크 (트리 높이만큼 위로)
            if not self.transparency_needed:
                self.transparency_needed = True
                self.image = self.original_image.copy()
                self.image.set_alpha(127)
            return True
                
        elif self.transparency_needed:
            self.transparency_needed = False
            self.image = self.original_image.copy()
            self.image.set_alpha(255)
        return False
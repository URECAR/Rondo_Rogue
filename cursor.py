# cursor.py
import pygame
from properties import *
from support import SoundManager, InputManager
from database import CharacterDatabase, SOUND_PROPERTIES
from ui import ConfirmationDialog

class Cursor(pygame.sprite.Sprite):
    def __init__(self, pos, groups, level):
        super().__init__(groups)
        self.sprite_type = 'HPBar'
        self.input_manager = InputManager()
        self.sound_manager = SoundManager()
        
        self.move_sound_path = '../audio/SE/cursor_move.ogg'
        
        # Basic cursor attributes
        self.level = level
        self.level_data = level.level_data
        self.image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=pygame.math.Vector2(pos[0] * TILESIZE,pos[1] * TILESIZE))
        # collision_rect 추가 - 기본 rect와 동일하게 설정
        self.collision_rect = self.rect.copy()
        self.pos = pygame.math.Vector2(pos[0], pos[1])
        self.previous_pos = self.pos.copy()
        # Control flags
        self.SW_select = False
        self.move_lock = False
        self.select_lock = False
        self.ismoving = False
        self.clicked_self = False
        self.click_move_speed = 60        # 클릭 이동 속도
        self.is_click_moving = False      # 클릭 이동 중인지 여부
        # Movement variables
        self.move_cooldown = 300
        self.move_timer = 0
        self.move_per_tile = 20
        self.Goto = pygame.math.Vector2()
        self.held_key = None  # 현재 누르고 있는 키 저장
        self.drag_start_pos = None
        self.is_dragging = False
        self.last_drag_pos = None
        self.drag_cooldown = 100  # 드래그 중 경로 생성 쿨다운 (밀리초)
        self.last_drag_time = 0   # 마지막 드래그 경로 생성 시간
        # Display priority
        self.priority = self.level_data["Map_Max_y"]
    
        self.cached_image = None
        self.cached_selection_state = False

    def handle_input(self):
        current_time = pygame.time.get_ticks()
        
        # 방향키 매핑
        direction_moves = {
            'Up': (0, -1),
            'Left': (-1, 0),
            'Down': (0, 1),
            'Right': (1, 0)
        }
        if not self.move_lock:
            mouse_pos = self.input_manager.get_mouse_pos()
            real_x = mouse_pos.x + self.level.visible_sprites.offset.x
            real_y = mouse_pos.y + self.level.visible_sprites.offset.y
            tile_x = int(real_x // TILESIZE)
            tile_y = int(real_y // TILESIZE)
            
            # 왼쪽 버튼을 누르고 있는 동안
            if self.input_manager.mouse_buttons[0]:
                if not self.is_dragging:
                    # 드래그 시작
                    self.drag_start_pos = pygame.math.Vector2(tile_x, tile_y)
                    self.is_dragging = True
                    self.last_drag_pos = self.drag_start_pos
                elif (current_time - self.last_drag_time >= self.drag_cooldown and 
                      (tile_x, tile_y) != (self.last_drag_pos.x, self.last_drag_pos.y)):
                    # 드래그 중 새로운 위치로 이동
                    target_x = (tile_x * TILESIZE) - self.rect.x
                    target_y = (tile_y * TILESIZE) - self.rect.y
                    self.Goto = pygame.math.Vector2(target_x, target_y)
                    self.pos = pygame.math.Vector2(tile_x, tile_y)
                    self.last_drag_pos = pygame.math.Vector2(tile_x, tile_y)
                    self.last_drag_time = current_time
                    self.is_click_moving = True
            else:
                # 드래그 종료
                self.is_dragging = False
                self.drag_start_pos = None
                self.last_drag_pos = None
        # 키가 눌린 상태이고 쿨다운이 지났다면 연속 이동
        if (self.held_key and current_time - self.move_timer >= self.move_cooldown and not self.move_lock and self.Goto.magnitude() == 0):
            dx, dy = direction_moves[self.held_key]
            self.Goto.x += dx * TILESIZE
            self.Goto.y += dy * TILESIZE
            # self.pos = pygame.math.Vector2((self.rect.topleft[0] + self.Goto.x) // TILESIZE, (self.rect.topleft[1] + self.Goto.y) // TILESIZE)
        
        
        # 새로운 방향키 입력 (처음 누를 때)
        for direction in direction_moves:
            if self.input_manager.is_just_pressed(direction) and not self.move_lock:
                dx, dy = direction_moves[direction]
                self.Goto.x += dx * TILESIZE
                self.Goto.y += dy * TILESIZE
                # self.pos = pygame.math.Vector2((self.rect.topleft[0] + self.Goto.x) // TILESIZE,(self.rect.topleft[1] + self.Goto.y) // TILESIZE)
                self.held_key = direction
                self.move_timer = current_time
                break
            
        if not self.move_lock and self.Goto.magnitude() == 0:
            if self.input_manager.is_left_click():
                mouse_pos = self.input_manager.get_mouse_pos()
                real_x = mouse_pos.x + self.level.visible_sprites.offset.x
                real_y = mouse_pos.y + self.level.visible_sprites.offset.y
                
                tile_x = int(real_x // TILESIZE)
                tile_y = int(real_y // TILESIZE)
                
                if (0 <= tile_x < self.level_data["Map_Max_x"] // TILESIZE and 0 <= tile_y < self.level_data["Map_Max_y"] // TILESIZE):
                    
                    map_action = self.level.map_action
                    # 현재 커서 위치가 이동경로의 끝점이고, 그 위치를 클릭했을 때
                    if (tile_x == self.pos.x and tile_y == self.pos.y and
                        map_action.current_state == 'player_control' and map_action.move_roots and map_action.move_roots[-1][0].pos == self.pos):
                        self.clicked_self = True

                    # 배틀러 위치에서 클릭했을 때
                    elif tile_x == self.pos.x and tile_y == self.pos.y:
                        self.clicked_self = True
                    else:
                        # 일반적인 커서 이동
                        target_x = (tile_x * TILESIZE) - self.rect.x
                        target_y = (tile_y * TILESIZE) - self.rect.y
                        self.Goto = pygame.math.Vector2(target_x, target_y)
                        self.pos = pygame.math.Vector2(tile_x, tile_y)
                        self.is_click_moving = True
        # 키를 뗐을 때
        if self.held_key and self.input_manager.is_just_released(self.held_key):
            self.held_key = None
            self.move_timer = 0
            
        # Cancel 키 처리
        if self.input_manager.is_just_pressed('Cancel'):
            # 대화상자가 떴을 땐 버튼 적용 안됨.
            if hasattr(self.level.map_action, 'current_dialog') and self.level.map_action.current_dialog:
                return
            if self.SW_select:
                
                if self.level.map_action.current_state == 'player_control' and self.level.map_action.selected_battler:
                    selected_battler = self.level.map_action.selected_battler
                    if [selected_battler.collision_rect.centerx, selected_battler.collision_rect.centery] != [self.rect.centerx, self.rect.centery]:
                        self.rect.center = pygame.math.Vector2(selected_battler.collision_rect.center)
                        self.Goto = pygame.math.Vector2(0,0)
                        self.pos = pygame.math.Vector2(self.rect.centerx // TILESIZE, self.rect.centery // TILESIZE)
                    else:
                        self.SW_select = False
                elif self.level.map_action.current_state in ['explore', 'look_bject']:
                    self.SW_select = False
            self.held_key = None
            self.move_timer = 0
            
# Select 키 처리 (이동 중이 아닐 때만)
        if not self.select_lock and not self.move_lock and self.Goto.magnitude() == 0:
            if (self.input_manager.is_just_pressed('Select') or self.clicked_self):
                if self.clicked_self and not self.SW_select:
                    self.clicked_self = False
                self.SW_select = True
            if self.level.map_action.current_state == 'explore': 
                # Previous/Next 키 처리
                wheel_movement = self.input_manager.get_wheel_movement()
                if self.input_manager.is_just_pressed('Previous') or self.input_manager.is_just_pressed('Next') or wheel_movement != 0:
                    wheel_movement = 0
                    direction = 'Previous' if (self.input_manager.is_just_pressed('Previous') or wheel_movement == 1) else 'Next'
                    actable_allies = [battler for battler in self.level.battler_sprites if battler.team == 'Ally' and not battler.inactive]
                    
                    # CharacterBase 순서대로 정렬
                    actable_allies.sort(key=lambda x: list(CharacterDatabase.data.keys()).index(x.char_type))
                    # 현재 커서 위치의 배틀러 찾기
                    current_battler = None
                    for battler in actable_allies:
                        if battler.pos == self.pos:
                            current_battler = battler
                            break

                    delta = 1 if direction == 'Next' else -1
                    next_index = (actable_allies.index(current_battler) + delta) % len(actable_allies) if current_battler else (0 if direction == 'Next' else len(actable_allies) - 1)
                    
                    # 커서 이동
                    next_battler = actable_allies[next_index]
                    self.level.visible_sprites.focus_on_target(next_battler,cursor_obj=self)   

    def move(self):
        if self.Goto.magnitude() > 0:
            self.ismoving = True
            # 이전 위치 저장
            old_pos = pygame.math.Vector2(self.rect.topleft)
            
            # 맵 경계 체크
            if self.rect.left <= 0 and self.Goto.x < 0:
                self.rect.left, self.Goto.x = 0, 0
                self.collision_rect.left = self.rect.left  # collision_rect도 함께 업데이트
            elif self.rect.right >= self.level_data["Map_Max_x"] and self.Goto.x > 0:
                self.rect.right = self.level_data["Map_Max_x"]
                self.collision_rect.right = self.rect.right  # collision_rect도 함께 업데이트
                self.Goto.x = 0
            if self.rect.top <= 0 and self.Goto.y < 0:
                self.rect.top, self.Goto.y = 0, 0
                self.collision_rect.top = self.rect.top  # collision_rect도 함께 업데이트
            elif self.rect.bottom >= self.level_data["Map_Max_y"] and self.Goto.y > 0:
                self.rect.bottom = self.level_data["Map_Max_y"]
                self.collision_rect.bottom = self.rect.bottom  # collision_rect도 함께 업데이트
                self.Goto.y = 0
                
            # 이동 처리
            self.pos = pygame.math.Vector2((self.rect.topleft[0] + self.Goto.x) // TILESIZE,
                                     (self.rect.topleft[1] + self.Goto.y) // TILESIZE)
        
        # 클릭 이동인 경우 더 빠른 속도 사용
            move_speed = self.click_move_speed if self.is_click_moving else self.move_per_tile
            
            move_x = min(move_speed, abs(self.Goto.x)) * (-1 if self.Goto.x < 0 else 1)
            move_y = min(move_speed, abs(self.Goto.y)) * (-1 if self.Goto.y < 0 else 1)
            
            self.rect.x += move_x
            self.rect.y += move_y
            self.collision_rect.x = self.rect.x
            self.collision_rect.y = self.rect.y
            self.Goto -= pygame.math.Vector2(move_x, move_y)
            
            if self.Goto.magnitude() == 0:
                self.ismoving = False
                self.is_click_moving = False  # 이동 완료 시 클릭 이동 상태 해제
                
                # 이동 완료 시 사운드 재생
                if not self.move_lock and self.previous_pos != self.pos:
                    self.sound_manager.play_sound(**SOUND_PROPERTIES['CURSOR_MOVE'])                
                    self.previous_pos = self.pos.copy()                

    def draw_rect(self):
        if self.cached_image is None or self.cached_selection_state != self.SW_select:
            self.cached_selection_state = self.SW_select
            self.cached_image = pygame.Surface((TILESIZE, TILESIZE), pygame.SRCALPHA)
            if self.SW_select:
                # Draw selected cursor
                pygame.draw.rect(self.cached_image, CURSOR_SELECTED_COLOR, (0, 0, TILESIZE, TILESIZE), 8)
                pygame.draw.rect(self.cached_image, CURSOR_BASIC_COLOR, pygame.Rect(3, 3, TILESIZE - 6, TILESIZE - 6), 2)
                pygame.draw.rect(self.cached_image, (0,0,0,0), (16, 0, 32, 64))
                pygame.draw.rect(self.cached_image, (0,0,0,0), (0, 16, 64, 32))
            else:
                # Draw basic cursor
                pygame.draw.rect(self.cached_image, CURSOR_BORDER_COLOR, (0, 0, TILESIZE, TILESIZE), 8)
                pygame.draw.rect(self.cached_image, CURSOR_BASIC_COLOR, pygame.Rect(3, 3, TILESIZE - 6, TILESIZE - 6), 2)
                pygame.draw.rect(self.cached_image, (0,0,0,0), (16, 0, 32, 64))
                pygame.draw.rect(self.cached_image, (0,0,0,0), (0, 16, 64, 32))

        self.image = self.cached_image.copy()
            
    def update(self):
        self.handle_input()
        self.move()
        self.draw_rect()
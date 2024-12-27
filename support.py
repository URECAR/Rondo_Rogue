# support.py
        
import pygame
from properties import *
from csv import reader
from os import walk            
import os
from typing import Dict, Optional
from database import SOUND_PROPERTIES
import math
class SoundManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SoundManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
            
    def __init__(self):
        if self._initialized:
            return
            
        # 초기화
        pygame.mixer.init()
        
        # 사운드 캐시 딕셔너리
        self.sound_cache = {}
        
        # 기본 볼륨 설정
        self.master_volume = 0.7  # 전체 볼륨 (0.0 ~ 1.0)
        self.bgm_volume = 0.4     # BGM 볼륨 (0.0 ~ 1.0)
        self.sfx_volume = 0.4     # 효과음 볼륨 (0.0 ~ 1.0)
        
        # 현재 재생 중인 BGM 트랙
        self.current_bgm = None
        self.current_bgm_path = None
        
        self._initialized = True
    
    def set_master_volume(self, volume):
        """전체 볼륨 설정 (0.0 ~ 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        # BGM 볼륨 업데이트
        pygame.mixer.music.set_volume(self.master_volume * self.bgm_volume)
        # 효과음 볼륨 업데이트
        for sound in self.sound_cache.values():
            sound.set_volume(self.master_volume * self.sfx_volume)
    
    def set_bgm_volume(self, volume):
        """BGM 볼륨 설정 (0.0 ~ 1.0)"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.master_volume * self.bgm_volume)
    
    def set_sfx_volume(self, volume):
        """효과음 볼륨 설정 (0.0 ~ 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        for sound in self.sound_cache.values():
            sound.set_volume(self.master_volume * self.sfx_volume)
    
    def load_sound(self, path):
        """사운드 파일 로드 및 캐시"""
        if path in self.sound_cache:
            return self.sound_cache[path]
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"Sound file not found: {path}")
        
        try:
            sound = pygame.mixer.Sound(path)
            sound.set_volume(self.master_volume * self.sfx_volume)
            self.sound_cache[path] = sound
            return sound
        except pygame.error as e:
            raise Exception(f"Failed to load sound: {path}. Error: {str(e)}")
    
    def play_sound(self, path, volume=1.0, delay=0):
        """효과음 재생"""
        try:
            sound = self.load_sound(path)
            sound.set_volume(volume * self.master_volume * self.sfx_volume)
            
            if delay > 0:
                pygame.time.set_timer(
                    pygame.event.Event(
                        pygame.USEREVENT, 
                        {'sound': sound}
                    ), 
                    int(delay * 1000),
                    1
                )
            else:
                sound.play()
        except Exception as e:
            print(f"Error playing sound: {str(e)}")
    
    def play_bgm(self, path, volume=1.0, delay=0, loop=True):
        """BGM 재생"""
        try:
            if self.current_bgm_path == path:
                return
                
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.master_volume * self.bgm_volume * volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self.current_bgm_path = path
            
        except Exception as e:
            print(f"Error playing BGM: {str(e)}")
    
    def stop_bgm(self):
        """BGM 정지"""
        pygame.mixer.music.stop()
        self.current_bgm_path = None
    
    def handle_event(self, event):
        """지연된 사운드 재생을 위한 이벤트 처리"""
        if event.type == pygame.USEREVENT and hasattr(event, 'sound'):
            event.sound.play()
    
    def clear_cache(self):
        """사운드 캐시 정리"""
        self.sound_cache.clear()

class InputManager:
    _instance = None
    
    # 인스턴스 객체는 1개만 생성으로 제한
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InputManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        self.sound_manager = SoundManager()
        self.pressed_keys = {}  # 현재 눌린 키 상태
        self.previous_keys = {} # 이전 프레임의 키 상태
        self.mouse_pos = pygame.math.Vector2(0, 0)
        self.mouse_buttons = [False, False, False]  # 왼쪽, 휠, 오른쪽
        self.previous_mouse_buttons = [False, False, False]
        self.mouse_click_pos = None  # 클릭이 발생한 위치
        self.mouse_wheel = 0  # 마우스 휠 움직임 저장
        # KEY_SETS의 모든 키에 대해 상태 초기화
        for key_group in KEY_SETS.values():
            if isinstance(key_group, list):
                for key in key_group:
                    self.pressed_keys[key] = False
                    self.previous_keys[key] = False
            else:
                self.pressed_keys[key_group] = False
                self.previous_keys[key_group] = False
    
    def handle_input(self, event):
        """이벤트 처리"""
        if event.type == pygame.MOUSEWHEEL:
            self.mouse_wheel = event.y  # y값이 양수면 위로, 음수면 아래로
        elif event.type == pygame.KEYDOWN:
            if event.key in self.pressed_keys:
                self.pressed_keys[event.key] = True
                # Select 키가 눌렸을 때 소리 재생
                if event.key in KEY_SETS.get('Select', []):
                    self.sound_manager.play_sound(**SOUND_PROPERTIES['CURSOR_SELECT'])
                if event.key in KEY_SETS.get('Cancel', []):
                    self.sound_manager.play_sound(**SOUND_PROPERTIES['CURSOR_CANCEL'])
        elif event.type == pygame.KEYUP:
            if event.key in self.pressed_keys:
                self.pressed_keys[event.key] = False
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = pygame.math.Vector2(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button <= 3:
                self.mouse_buttons[event.button-1] = True
                self.mouse_click_pos = pygame.math.Vector2(event.pos)
                if event.button == 1:  # 좌클릭
                    self.sound_manager.play_sound(**SOUND_PROPERTIES['CURSOR_CLICK'])
                elif event.button == 3:  # 우클릭
                    self.sound_manager.play_sound(**SOUND_PROPERTIES['CURSOR_CANCEL'])
                    for key in KEY_SETS['Cancel']:
                        self.pressed_keys[key] = True
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button <= 3:
                self.mouse_buttons[event.button-1] = False
                if event.button == 3:
                    for key in KEY_SETS['Cancel']:
                        self.pressed_keys[key] = False
                self.mouse_click_pos = None
    
    def update(self):
        """이전 상태 업데이트"""
        self.previous_keys = self.pressed_keys.copy()
        self.previous_mouse_buttons = self.mouse_buttons.copy()
    
    def is_pressed(self, action):
        keys = KEY_SETS[action]
        if isinstance(keys, list):
            return any(self.pressed_keys.get(k, False) for k in keys)
        return self.pressed_keys.get(keys, False)

    def is_just_pressed(self, action):
        keys = KEY_SETS[action]
        if isinstance(keys, list):
            return any(self.pressed_keys.get(k, False) and not self.previous_keys.get(k, False) for k in keys)
        return self.pressed_keys.get(keys, False) and not self.previous_keys.get(keys, False)

    def is_just_released(self, action):
        keys = KEY_SETS[action]
        if isinstance(keys, list):
            return any(not self.pressed_keys.get(k, False) and self.previous_keys.get(k, False) for k in keys)
        return not self.pressed_keys.get(keys, False) and self.previous_keys.get(keys, False)
    # 새로운 마우스 관련 메서드들
    def get_mouse_pos(self):
        """현재 마우스 위치 반환"""
        return self.mouse_pos

    def get_click_pos(self):
        """클릭이 발생한 위치 반환"""
        return self.mouse_click_pos
    
    def get_wheel_movement(self):
        """마우스 휠 움직임 반환 후 리셋"""
        wheel = self.mouse_wheel
        self.mouse_wheel = 0
        return wheel
    
    def is_left_click(self):
        """왼쪽 버튼이 이번 프레임에 클릭되었는지"""
        return self.mouse_buttons[0] and not self.previous_mouse_buttons[0]

    def is_right_click(self):
        """오른쪽 버튼이 이번 프레임에 클릭되었는지"""
        return self.mouse_buttons[2] and not self.previous_mouse_buttons[2]

    def is_mouse_in_rect(self, rect):
        """마우스가 특정 영역 안에 있는지 확인"""
        return rect.collidepoint(self.mouse_pos)
    
    def reset_mouse_state(self):
        """마우스 상태를 강제로 초기화"""
        self.mouse_buttons = [False, False, False]
        self.mouse_click_pos = None
        self.mouse_wheel = 0
        self.is_dragging = False  # 커서에서 사용하는 드래그 상태도 초기화

    # def reset_input_state(self):
    #     """모든 입력 상태 초기화"""
    #     for key in self.pressed_keys:
    #         self.pressed_keys[key] = False
    #     for key in self.previous_keys:
    #         self.previous_keys[key] = False
    #     self.mouse_buttons = [False, False, False]
    #     self.previous_mouse_buttons = [False, False, False]
    #     self.mouse_click_pos = None
    #     self.mouse_wheel = 0

def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map,delimiter = ',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map
    
def import_folder(path):
    surface_list = []

    for _,__,img_files in walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)
            
    return surface_list

def determine_direction(prev_pos, current_pos):
    """두 위치 사이의 방향을 결정"""
    dx = current_pos[0] - prev_pos[0]
    dy = current_pos[1] - prev_pos[1]
    
    if dx > 0: return 'right'
    if dx < 0: return 'left'
    if dy > 0: return 'down'
    if dy < 0: return 'up'
 
 
            
class MessageDialog:
    def __init__(self, messages, font, level):
        self.messages = messages
        self.font = font
        self.level = level
        self.display_surface = pygame.display.get_surface()
        
        # Dialog box properties
        self.width = WIDTH - 400
        self.height = 200
        self.x = 200
        self.y = HEIGHT - self.height - 50
        
        # Text properties
        self.current_message = ""
        self.target_message = messages[0] if messages else ""
        self.char_index = 0
        self.char_speed = 2  # Characters per frame
        self.finished = False
        
        # Calculate text wrapping
        self.max_line_width = self.width - 40
        self.line_height = self.font.get_height() + 5
            
    def render(self):
        # Draw dialog box
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(self.display_surface, (0, 0, 0, 180), dialog_rect, border_radius=10)
        pygame.draw.rect(self.display_surface, (255, 255, 255), dialog_rect, 3, border_radius=10)
        
        # Wrap and render text
        words = self.current_message.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if self.font.size(test_line)[0] <= self.max_line_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        # Draw text
        for i, line in enumerate(lines):
            text_surface = self.font.render(line, True, (255, 255, 255))
            self.display_surface.blit(text_surface, (self.x + 20, self.y + 20 + i * self.line_height))
        
        # Draw continue indicator if message is complete
        if self.finished:
            continue_surface = self.font.render("▼", True, (255, 255, 255))
            self.display_surface.blit(continue_surface, 
                (self.x + self.width - 30, self.y + self.height - 30))
    
    def finish_current_message(self):
        """Immediately display the full message"""
        self.char_index = len(self.target_message)
        self.current_message = self.target_message
        self.finished = True
    def update(self):
        if not self.finished and self.char_index < len(self.target_message):
            self.char_index += self.char_speed
            self.current_message = self.target_message[:self.char_index]
            if self.char_index >= len(self.target_message):
                self.finished = True

    def handle_input(self, input_manager):
        total_length = 0
        if self.current_message_index < len(self.parsed_messages):
            total_length = sum(len(section['text']) for section in 
                             self.parsed_messages[self.current_message_index])

        # Handle instant display
        if input_manager.is_just_pressed('Cancel'):
            self.is_instant = True
            return None

        # Handle message advancement
        if input_manager.is_just_pressed('Select') or input_manager.is_left_click():
            if self.current_char_index >= total_length:
                self.current_message_index += 1
                self.current_char_index = 0
                self.is_instant = False
                if self.current_message_index >= len(self.parsed_messages):
                    return 'close'
            else:
                self.is_instant = True

        return None
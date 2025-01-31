# support.py
import pygame
from properties import *
import os
from database import EQUIP_PROPERTIES, SKILL_PROPERTIES, STATUS_PROPERTIES, SOUND_PROPERTIES
from common_method import print_if

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
        self.master_volume = INITIAL_MASTER_VOLUME  # 전체 볼륨 (0.0 ~ 1.0)
        self.bgm_volume = INITIAL_MUSIC_VOLUME     # BGM 볼륨 (0.0 ~ 1.0)
        self.sfx_volume = INITIAL_SFX_VOLUME     # 효과음 볼륨 (0.0 ~ 1.0)
        
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
            print_if(self.SW_debug,f"Error playing sound: {str(e)}")
    
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
            print_if(self.SW_debug,f"Error playing BGM: {str(e)}")
    
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

class EventManager:
    def __init__(self):
        self.triggered_events = set()

    def trigger_event(self, event_name):
        if event_name not in self.triggered_events:
            self.triggered_events.add(event_name)
            return True
        return False

class Effect:
    def __repr__(self):
        """Effect 객체의 기본 출력 형태"""
        # 기본 정보
        effect_str = ""
        
        # passive
        if self.type == 'passive':
            if self.source:
                source_str = self.source
                source_str = source_str.replace("passive_", "")
                effect_str = f"{source_str}: "
            
            effects_str = []
            for stat, value in self.effects.items():
                if self.is_percent:
                    effects_str.append(f"{stat}: {value:+}%")
                else:
                    effects_str.append(f"{stat}: {value:+}")
            effect_str += ", ".join(effects_str)
            
        # passive_conditional
        elif self.type == 'passive_conditional':
            if self.source:
                source_str = self.source
                source_str = source_str.replace("passive_conditional_", "")
                effect_str = f"{source_str}: "
            
            effects_str = []
            for stat, value in self.effects.items():
                if self.is_percent:
                    effects_str.append(f"{stat}: {value:+}%")
                else:
                    effects_str.append(f"{stat}: {value:+}")
            effect_str += ", ".join(effects_str)
            
            # 활성화 여부는 조건이 있는지만 표시
            if self.condition:
                effect_str += " (조건부 활성)"
        
        # 그 외 타입
        else:
            effect_str = f"[{self.type}] "
            if self.source:
                effect_str += f"from {self.source}: "
            effects_str = []
            for stat, value in self.effects.items():
                if self.is_percent:
                    effects_str.append(f"{stat}: {value:+}%")
                else:
                    effects_str.append(f"{stat}: {value:+}")
            effect_str += ", ".join(effects_str)
        
        # 남은 턴수 표시
        if self.remaining_turns is not None:
            effect_str += f" ({self.remaining_turns} turns left)"
        
        return effect_str

    def __init__(self, 
                effect_type,           # 'passive', 'buff', 'status', 'equipment', 'passive_conditional'
                effects,               # {'stat': value} 형태의 효과
                source=None,           # 효과의 출처 (스킬명, 아이템명 등)
                remaining_turns=None,  # None이면 영구 지속
                condition=None,        # 조건부 효과를 위한 조건
                is_percent=False):     # 퍼센트 기반 효과인지 여부
        self.SW_debug = False
        print_if(self.SW_debug,f"\n[Creating Effect]")
        print_if(self.SW_debug,f"Type: {effect_type}")
        print_if(self.SW_debug,f"Source: {source}")
        print_if(self.SW_debug,f"Effects: {effects}")
        print_if(self.SW_debug,f"Condition: {condition}")
        print_if(self.SW_debug,f"Remaining turns: {remaining_turns}")
        print_if(self.SW_debug,f"Is percent: {is_percent}")

        self.type = effect_type
        self.effects = effects
        self.source = source
        self.remaining_turns = remaining_turns
        self.condition = condition
        self.is_percent = is_percent

    def check_condition(self, battler):
        """조건 충족 여부 확인"""
        if not self.condition:
            return True

        target = self.condition.get('target')
        stat = self.condition.get('stat')
        check_types = self.condition.get('check_type', [])
        threshold = self.condition.get('threshold', 0)

        # 현재는 target이 'self'인 경우만 고려
        if target == 'self':
            # activate_condition과 stats에서 stat 값을 검색
            value_activate = battler.activate_condition.get(stat, 0)
            value_stats = battler.stats.get(stat, 0)
            current_value = value_activate + value_stats
            print_if(self.SW_debug,"현재값:"+str(current_value))
            print_if(self.SW_debug,"역치값:"+str(threshold))
            # check_types 중 하나라도 만족하면 True
            for ctype in check_types:
                if ctype.lower() == 'equal' and current_value == threshold:
                    return True
                elif ctype.lower() == 'more' and current_value >= threshold:
                    return True
                elif ctype.lower() == 'less' and current_value < threshold:
                    return True
            return False

        # 다른 타겟 로직 필요한 경우 추가
        return True

class EffectManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EffectManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.SW_debug = False

    def add_effect(self, battler, effect):
        """캐릭터에 새로운 효과 추가"""
        if not hasattr(battler, 'effects'):
            battler.effects = []
            
        # 동일 출처의 기존 효과 제거
        if effect.source:
            battler.effects = [e for e in battler.effects if e.source != effect.source]
            
        battler.effects.append(effect)

        
        self.update_effects(battler)

    def remove_effect(self, battler, source=None, effect_type=None):
        """특정 출처나 타입의 효과 제거"""
        if not hasattr(battler, 'effects'):
            return
            
        if source:
            battler.effects = [e for e in battler.effects if e.source != source]
        if effect_type:
            battler.effects = [e for e in battler.effects if e.type != effect_type]
            
        self.update_effects(battler)

    def elapse_turn(self, battler):
        """해당 배틀러의 모든 효과 턴 수 감소"""
        if not hasattr(battler, 'effects'):
            return

        # 지속시간이 있는 효과들의 턴 감소 및 종료 처리
        remaining_effects = []
        for effect in battler.effects:
            if effect.remaining_turns is None:  # 영구 효과
                remaining_effects.append(effect)
                continue
                
            effect.remaining_turns -= 1  # 턴 감소
            if effect.remaining_turns > 0:  # 아직 지속시간 남음
                remaining_effects.append(effect)
        
        battler.effects = remaining_effects
                         
        self.update_effects(battler)

    def update_effects(self, battler):
        """효과 적용하여 스탯 재계산"""
        
        battler.activate_condition['HP_ratio'] = battler.Cur_HP / battler.stats['Max_HP'] * 100
        battler.activate_condition['MP_ratio'] = battler.Cur_MP / battler.stats['Max_MP'] * 100
        
        
        if not hasattr(battler, 'effects'):
            battler.effects = []

        print_if(self.SW_debug,f"\n[Effect Update for {battler.name}]")
        print_if(self.SW_debug,f"Total effects count: {len(battler.effects)}")
        print_if(self.SW_debug,"Current effects list:")
        for effect in battler.effects:
            print_if(self.SW_debug,f"- Type: {effect.type}, Source: {effect.source}")
            if effect.condition:
                print_if(self.SW_debug,f"  Has condition: {effect.condition}")

        # 기본 스탯으로 초기화
        battler.stats = battler.base_stats.copy()
        percent_mods = {}
        flat_mods = {}
        
        # 효과 처리
        for effect in battler.effects:
            print_if(self.SW_debug,f"\nProcessing effect: {effect.source}")
            
            # 조건부 효과 체크
            if effect.condition:
                print_if(self.SW_debug,f"Checking condition for {effect.source}")
                if not effect.check_condition(battler):
                    print_if(self.SW_debug,f"- Condition check failed for {effect.source}")
                    continue
                print_if(self.SW_debug,f"- Condition check passed for {effect.source}")

            if effect.is_percent:
                for stat, mod in effect.effects.items():
                    percent_mods[stat] = percent_mods.get(stat, 0) + mod
                    print_if(self.SW_debug,f"- Added {mod}% to {stat}")
            else:
                for stat, mod in effect.effects.items():
                    flat_mods[stat] = flat_mods.get(stat, 0) + mod
                    print_if(self.SW_debug,f"- Added {mod} to {stat}")

        print_if(self.SW_debug,"\nFinal modifications:")
        print_if(self.SW_debug,f"Percent mods: {percent_mods}")
        print_if(self.SW_debug,f"Flat mods: {flat_mods}")

        # 퍼센트 수정치 적용
        for stat, total_percent in percent_mods.items():
            if stat in battler.stats:
                old_value = battler.stats[stat]
                battler.stats[stat] *= (1 + total_percent/100)
                print_if(self.SW_debug,f"{stat}: {old_value} -> {battler.stats[stat]} ({total_percent}% mod)")

        # 고정값 수정치 적용
        for stat, mod in flat_mods.items():
            if stat in battler.stats:
                old_value = battler.stats[stat]
                battler.stats[stat] += mod
                print_if(self.SW_debug,f"{stat}: {old_value} -> {battler.stats[stat]} ({mod} mod)")

        # multiplier 관련 스탯은 최소값 0.2로 보정
        for stat in battler.stats:
            if 'mul' in stat.lower():
                if battler.stats[stat] < 0.2:
                    print_if(self.SW_debug,f"Correcting {stat} from {battler.stats[stat]} to 0.2 (minimum)")
                    battler.stats[stat] = 0.2

        # 정수형 스탯 처리
        integer_stats = ['Max_HP', 'Max_MP', 'STR', 'DEX', 'INT', 'RES', 'Mov', 'CHA']
        for stat in integer_stats:
            if stat in battler.stats:
                old_value = battler.stats[stat]
                battler.stats[stat] = int(battler.stats[stat])
                if old_value != battler.stats[stat]:
                    print_if(self.SW_debug,f"Rounded {stat}: {old_value} -> {battler.stats[stat]}")

        # 상태이상 효과 처리
        status_effects = [effect for effect in battler.effects if effect.type == 'status']
        if status_effects:
            print_if(self.SW_debug,"\nStatus effects found:", [effect.source for effect in status_effects])
            
        battler.force_inactive = any('동결' in effect.source for effect in status_effects)
        if battler.force_inactive:
            print_if(self.SW_debug,f"{battler.name} is now force_inactive due to status effect")
            battler.inactive = True 

    def get_active_effects(self, battler, effect_type=None):
        """캐릭터의 현재 활성화된 효과 목록 반환"""
        if not hasattr(battler, 'effects'):
            return []
            
        if effect_type:
            return [effect for effect in battler.effects 
                   if effect.type == effect_type and 
                   (effect.type != 'passive_conditional' or 
                    effect.check_condition(battler))]
        return [effect for effect in battler.effects 
               if effect.type != 'passive_conditional' or 
               effect.check_condition(battler)]
               
    def get_active_status(self, battler):
        """현재 적용 중인 상태이상 반환"""
        status_effects = [effect for effect in battler.effects 
                         if effect.type == 'status']
        if not status_effects:
            return None
        # 가장 최근에 적용된 상태이상 반환
        return status_effects[-1].source.replace('status_', '')

    def apply_temporary_buff(self, battler, buff_name, effects, duration=None):
        """임시 버프 효과 적용"""
        # 퍼센트 효과
        if 'percent' in effects:
            effect = Effect(
                effect_type='buff',
                effects=effects['percent'],
                source=f"temp_buff_{buff_name}",
                remaining_turns=duration,
                is_percent=True
            )
            self.add_effect(battler, effect)
        # 고정값 효과
        if 'flat' in effects:
            effect = Effect(
                effect_type='buff',
                effects=effects['flat'],
                source=f"temp_buff_{buff_name}",
                remaining_turns=duration
            )
            self.add_effect(battler, effect)

    def apply_passive_effects(self, battler):
        """패시브 효과를 적용"""
        for effect in battler.effects:
            if effect.type == 'passive_conditional':
                if effect.check_condition(battler):
                    # 조건을 충족한 경우 효과 적용
                    for stat, value in effect.effects.items():
                        if stat in battler.stats:
                            battler.stats[stat] += value
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
            text_rect = text_surface.get_rect(topleft=(self.x + 20, self.y + 20 + i * self.line_height))
            self.display_surface.blit(text_surface, text_rect)
        
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

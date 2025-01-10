# animation.py
import pygame
import os
from database import ANIMATION_PROPERTIES, SOUND_PROPERTIES
from properties import *
from support import SoundManager
class Animation(pygame.sprite.Sprite):
    def __init__(self, start_pos, animation_type, value=None,track_target=False):
        super().__init__()
        self.sprite_type = 'animation'
        self.animation_type = animation_type
        self.props = ANIMATION_PROPERTIES[animation_type]
        self.size = self.props['size']
        self.anchor = self.props['anchor']
        self.offset = self.props.get('offset', [0, 0])  # 기본값 [0, 0]
        self.last_update_time = pygame.time.get_ticks()
        self.sound_manager = SoundManager()
        # 추적 대상 저장
        self.track_target = track_target
        self.target = start_pos if isinstance(start_pos, pygame.sprite.Sprite) else None
        self.initial_offset = None  # 초기 위치와의 오프셋 저장
        if 'sound' in self.props:
            sound_key = self.props['sound']          
            self.sound_manager.play_sound(**SOUND_PROPERTIES[sound_key])
            
        if animation_type == 'SPREAD_LINE':
            self.split_time = self.props['split_time']
            self.split_speed = self.props['split_speed']
            self.elapsed_time = 0
            self.transparency = 255
            self.image_parts = []
            self.part_positions = []
            self.part_velocities = []


            # SPREAD_LINE은 항상 캐릭터의 원본 이미지 필요
            if isinstance(start_pos, pygame.sprite.Sprite):
                self.original_image = start_pos.image.copy()
                self.center_pos = (start_pos.rect.centerx, start_pos.rect.centery)
                self.rect = start_pos.rect.copy()
                self.setup_spread_animation()
            else:
                raise ValueError("SPREAD_LINE animation requires a sprite object")
                
        elif animation_type == 'DAMAGE' or animation_type == 'CRITICAL_DAMAGE':
            self.value = value
            self.elapsed_time = 0
            self.y_offset = 0
            self.setup_damage_animation(start_pos, type = animation_type)

        elif animation_type == 'PHASE_CHANGE':
            self.duration = self.props['duration']
            self.slide_speed = self.props['slide_speed']
            self.fade_in_duration = self.props['fade_in_duration']
            self.fade_out_duration = self.props['fade_out_duration']
            self.center_duration = self.props['center_duration']
            self.elapsed_time = 0
            self.camera_offset = value[0]
            
            # 이미지 로드
            if value[1] == 'Player':
                self.orig_image = pygame.image.load(f"{self.props['folder_path']}/PlayersPhase.png").convert_alpha()
            elif value[1] == 'Enemy':
                self.orig_image = pygame.image.load(f"{self.props['folder_path']}/EnemysPhase.png").convert_alpha()
            else:
                raise ValueError(f"Invalid phase value: {value}. Must be either 'Player' or 'Enemy'")
                
            self.original_width = self.orig_image.get_width()
            self.original_height = self.orig_image.get_height()
            self.image = pygame.transform.scale(self.orig_image,(self.original_width / 2,self.original_height / 2))
            
            # 화면 관련 초기 설정
            self.rect = self.image.get_rect()
            self.true_pos = pygame.math.Vector2(-self.original_width, HEIGHT // 2)  # True position in world space
            self.rect.midleft = self.true_pos
            self.alpha = 0
            
            # Priority for rendering
            self.priority = float('inf')  # Always render on top

        elif animation_type == 'STAT_CHANGE':
            self.setup_stat_change_animation(start_pos, value)
            self.priority = 9999

        elif animation_type == 'LEVEL_UP':
            # 공통 속성 초기화
            self.elapsed_time = 0
            
            # props에서 필요한 속성들 가져오기
            self.duration = self.props['duration']
            self.rise_height = self.props['rise_height']
            self.fade_in = self.props['fade_in']
            self.fade_out = self.props['fade_out']
            
            if isinstance(start_pos, pygame.sprite.Sprite):
                self.setup_level_up_animation(start_pos)
                # Level Up 애니메이션은 항상 최상단에 표시
                self.priority = float('inf')
            else:
                raise ValueError("LEVEL_UP animation requires a sprite object")

        else:
            # 일반 프레임 애니메이션
            self.frame_index = 0
            self.animation_speed = self.props['frame_speed']
            self.folder_path = self.props['folder_path']
            self.setup_frame_animation()
            self.rect = self.image.get_rect()
            
            # 위치 설정
            if isinstance(start_pos, tuple):
                base_pos = start_pos
            else:
                if self.anchor == 'center':
                    base_pos = start_pos.rect.center
                elif self.anchor == 'top':
                    base_pos = start_pos.rect.midbottom
                elif self.anchor == 'bottom':
                    base_pos = start_pos.rect.midtop
                else:
                    base_pos = start_pos.rect.topleft
                    
            # 앵커 포인트에 따른 위치 설정 + 오프셋 적용
            final_pos = (base_pos[0] + self.offset[0], base_pos[1] + self.offset[1])
            
            if self.anchor == 'center':
                self.rect.center = final_pos
            elif self.anchor == 'top':
                self.rect.midbottom = final_pos
            elif self.anchor == 'bottom':
                self.rect.midtop = final_pos
        if not hasattr(self, 'priority'):
            self.priority = self.rect.centery
            if 'priority_offset' in ANIMATION_PROPERTIES[animation_type]:
                self.priority += ANIMATION_PROPERTIES[animation_type]['priority_offset'] * TILESIZE
        if isinstance(start_pos, pygame.sprite.Sprite):
            if self.track_target:
                # 추적 모드일 때는 대상과의 상대적 위치 저장
                self.initial_offset = pygame.math.Vector2(
                    self.rect.centerx - start_pos.collision_rect.centerx,
                    self.rect.centery - start_pos.collision_rect.centery
                )
            else:
                # 고정 모드일 때는 현재 위치만 저장
                self.rect = self.image.get_rect(center=start_pos.rect.center)
                
    def update(self):
        if self.track_target and self.target and self.initial_offset:
            # 대상을 추적하는 애니메이션은 매 프레임마다 위치 업데이트
            self.rect.center = (
                self.target.collision_rect.centerx + self.initial_offset.x,
                self.target.collision_rect.centery + self.initial_offset.y
            )
        if self.animation_type == 'SPREAD_LINE':
            self.update_spread_animation()

        elif self.animation_type == 'DAMAGE' or self.animation_type == 'CRITICAL_DAMAGE':
            self.update_damage_animation()

        elif self.animation_type == 'PHASE_CHANGE':
            self.update_phase_change_animation()

        elif self.animation_type == 'STAT_CHANGE':
            self.update_stat_change_animation()

        elif self.animation_type == 'LEVEL_UP':  # LEVEL_UP 분기 추가
            self.update_level_up_animation()

        else:  # 프레임 기반 애니메이션
            self.update_frame_animation()

    def setup_frame_animation(self):
        """프레임 기반 애니메이션 로드"""
        self.animation_frames = []
        index = 0
        while True:
            image_path = f"{self.folder_path}/{index}.png"
            if os.path.exists(image_path):
                image = pygame.image.load(image_path).convert_alpha()
                scaled_width = int(image.get_width() * self.size)
                scaled_height = int(image.get_height() * self.size)
                self.animation_frames.append(pygame.transform.scale(image, (scaled_width, scaled_height)))
                index += 1
            else:
                break
        if not self.animation_frames:
            raise IsADirectoryError(f"애니메이션을 불러오지 못함: {self.folder_path}")
        self.image = self.animation_frames[0]

    def setup_damage_animation(self, start_pos,type):
        """데미지/힐 텍스트 애니메이션 설정"""
        # 폰트 및 색상 설정
        if type == 'DAMAGE':
            font = pygame.font.Font(UI_FONT, 36)
        elif type == 'CRITICAL_DAMAGE':
            font = pygame.font.Font(UI_FONT, 48)
        text = str(abs(int(self.value)))  # 절대값 사용
        
        # 힐링(양수)과 데미지(음수)에 따라 다른 색상 설정
        if self.value > 0:  # 힐링
            text = "+" + text  # 힐링은 + 기호 추가
            text_color = (0, 255, 0)  # 초록색
            outline_color = (255, 255, 255)  # 흰색
        else:  # 데미지
            if type == 'DAMAGE':
                text_color = (255, 0, 0)  # 빨간색
                outline_color = (0, 0, 0)  # 검은색
            elif type == 'CRITICAL_DAMAGE':
                text_color = (255, 215, 0)  # 금색
                outline_color = (255, 0, 0)  # 빨간 테두리
                glow_color = (255, 69, 0)  # 주황색 글로우
        
        # 메인 텍스트
        self.text_surface = font.render(text, True, text_color)
        
        # 테두리용 텍스트
        self.outline_positions = [(1,1), (-1,-1), (1,-1), (-1,1), (0,1), (0,-1), (1,0), (-1,0)]
        self.outline_surfaces = []
        for dx, dy in self.outline_positions:
            outline = font.render(text, True, outline_color)
            self.outline_surfaces.append((outline, (dx, dy)))

        # 이미지 초기화
        text_width = self.text_surface.get_width() + 2
        text_height = self.text_surface.get_height() + 2
        self.image = pygame.Surface((text_width, text_height), pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        # 위치 설정
        if isinstance(start_pos, tuple):
            self.rect.center = start_pos
        else:
            self.rect.center = (start_pos.rect.centerx, start_pos.rect.top - 20)
        
        self.start_x = float(self.rect.centerx)
        self.start_y = float(self.rect.centery)
        self.alpha = 255
        
        # 포물선 운동을 위한 속성
        self.time = 0
        self.horizontal_speed = self.props.get('horizontal_speed', 50)  # x축 이동 속도
        self.initial_velocity = self.props.get('initial_velocity', -150)  # 초기 수직 속도
        self.gravity = self.props.get('gravity', 400)  # 중력 가속도
        self.duration = self.props.get('duration', 1.0)  # 전체 지속시간

        # 우선순위 설정 - 화면 최상단에 표시되도록
        self.priority = float('inf')  # 무한대로 설정하여 항상 최상단에 표시

    def setup_spread_animation(self):
        """분산 애니메이션 초기 설정"""
        self.original_width, self.original_height = self.original_image.get_size()
        self.width = self.original_width * 2
        self.height = self.original_height * 2
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # 파트 크기 및 중심점 계산
        part_size = 8
        center_x = self.width // 2
        center_y = self.height // 2
        
        # 원본 이미지의 중심으로부터 파트 위치 계산
        for y in range(0, self.original_height, part_size):
            for x in range(0, self.original_width, part_size):
                # 파트 추출
                part = pygame.Surface((part_size, part_size), pygame.SRCALPHA)
                part.blit(self.original_image, (0, 0), (x, y, part_size, part_size))
                
                # 파트가 투명하지 않은 경우만 추가 (실제 이미지가 있는 부분만)
                if part.get_at((0, 0))[3] != 0:  # 알파값이 0이 아닌 경우
                    # 중심으로부터의 상대 위치 계산
                    rel_x = x - (self.original_width // 2)
                    rel_y = y - (self.original_height // 2)
                    
                    # 초기 위치 설정 (중앙 정렬)
                    init_x = center_x - (self.original_width // 2) + x
                    init_y = center_y - (self.original_height // 2) + y
                    
                    # 속도 계산 (중심에서 바깥쪽으로)
                    distance = max(1, (rel_x ** 2 + rel_y ** 2) ** 0.5)
                    vel_x = (rel_x / distance) * self.split_speed
                    vel_y = (rel_y / distance) * self.split_speed
                    
                    self.image_parts.append(part)
                    self.part_positions.append([init_x, init_y])
                    self.part_velocities.append([vel_x, vel_y])

        # rect 위치 설정
        self.rect = self.image.get_rect(center=self.center_pos)

    def setup_stat_change_animation(self, battler, value):
        """스탯/상태 변화 팝업 애니메이션 설정
        pos: Character 객체
        value: (stat_name, is_buff, offset) 튜플
        """
        font = pygame.font.Font(UI_FONT, 12)
        padding = 5
        if isinstance(value, tuple):
            stat_name, is_buff, offset = value
        else:
            stat_name = value  # 단일 값으로 stat_name을 받았을 때
            is_buff = None
            offset = 0
        
        # 텍스트와 색상 설정
        text = stat_name
        if isinstance(is_buff, bool):  # 스탯 변화인 경우
            text = f"{stat_name} {'↑' if is_buff else '↓'}"
            color = (150, 255, 150) if is_buff else (255, 150, 150)  # 초록 or 빨강
        else:  # 상태이상인 경우
            color = (255, 255, 100)  # 노란색
        
        # 텍스트 렌더링
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        # UI 배경 생성
        ui_width = text_rect.width + padding * 2
        ui_height = text_rect.height + padding * 2
        self.image = pygame.Surface((ui_width, ui_height), pygame.SRCALPHA)
        
        # 배경 채우기 (반투명)
        bg_color = (*color, 40)
        pygame.draw.rect(self.image, bg_color, (0, 0, ui_width, ui_height), border_radius=4)
        
        # 테두리 그리기
        border_color = (*color, 200)
        pygame.draw.rect(self.image, border_color, (0, 0, ui_width, ui_height), 2, border_radius=4)
        
        # 텍스트 중앙 배치
        text_pos = ((ui_width - text_rect.width) // 2, (ui_height - text_rect.height) // 2)
        self.image.blit(text_surface, text_pos)
        
        # 위치 설정
        self.rect = self.image.get_rect()
        self.rect.midleft = (battler.collision_rect.centerx + 32, battler.collision_rect.centery + offset)
        
        # 애니메이션 속성
        self.start_y = float(self.rect.centery)
        self.elapsed_time = 0
        self.duration = 1.5
        self.rise_speed = 30
        self.fade_in = 0.2
        self.fade_out = 0.3
           
    def setup_level_up_animation(self, battler):
        """레벨업 텍스트 애니메이션 설정"""
        font = pygame.font.Font(UI_FONT, self.props['font_size'])
        text = "Level Up!"
        
        # 메인 텍스트
        self.text_surface = font.render(text, True, self.props['font_color'])
        
        # 글로우 효과용 텍스트 (약간 큰 크기)
        glow_font = pygame.font.Font(UI_FONT, self.props['font_size'] + 2)
        self.glow_surface = glow_font.render(text, True, self.props['glow_color'])
        
        # 이미지 초기화
        text_width = max(self.text_surface.get_width(), self.glow_surface.get_width())
        text_height = max(self.text_surface.get_height(), self.glow_surface.get_height())
        self.image = pygame.Surface((text_width + 4, text_height + 4), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        # 시작 위치 설정 (캐릭터의 중앙)
        self.rect.center = battler.rect.center
        self.start_y = float(self.rect.centery)
        self.elapsed_time = 0
           
    def update_frame_animation(self):

        """프레임 기반 애니메이션 업데이트"""
        current_time = pygame.time.get_ticks()
        time_elapsed = (current_time - self.last_update_time) / 1000
        self.last_update_time = current_time

        self.frame_index += self.animation_speed * time_elapsed
        if self.frame_index >= len(self.animation_frames):
            self.kill()
        else:
            self.image = self.animation_frames[int(self.frame_index)]

    def update_damage_animation(self):
        """데미지 텍스트 애니메이션 업데이트"""
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time
        
        self.time += dt
        if self.time >= self.duration:
            self.kill()
            return

        # 포물선 운동 계산
        dx = self.horizontal_speed * self.time
        dy = self.initial_velocity * self.time + 0.5 * self.gravity * self.time * self.time
        
        # 새로운 위치 계산
        new_x = self.start_x + dx
        new_y = self.start_y + dy
        
        # 이미지 업데이트
        self.image.fill((0,0,0,0))
        
        # 페이드아웃 효과
        self.alpha = max(0, int(255 * (1 - self.time / self.duration)))
        
        # 테두리 그리기
        for surface, (dx, dy) in self.outline_surfaces:
            outline_copy = surface.copy()
            outline_copy.set_alpha(self.alpha)
            self.image.blit(outline_copy, (dx, dy))
        
        # 메인 텍스트 그리기
        text_copy = self.text_surface.copy()
        text_copy.set_alpha(self.alpha)
        self.image.blit(text_copy, (0, 0))
        
        # 위치 업데이트
        self.rect.centerx = int(new_x)
        self.rect.centery = int(new_y)

    def update_spread_animation(self):
        """분산 애니메이션 업데이트"""
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time
        
        self.elapsed_time += dt
        if self.elapsed_time >= self.split_time:
            self.kill()
            return
        
        # 투명도 계산 및 이미지 초기화
        alpha = max(0, int(255 * (1 - self.elapsed_time / self.split_time)))
        self.image.fill((0, 0, 0, 0))
        
        # 각 파트 업데이트
        for i, (part, pos, vel) in enumerate(zip(self.image_parts, self.part_positions, self.part_velocities)):
            # 위치 업데이트
            self.part_positions[i][0] += vel[0] * dt
            self.part_positions[i][1] += vel[1] * dt
            
            # 파트 복사 및 투명도 설정
            part_copy = part.copy()
            part_copy.set_alpha(alpha)
            
            # 업데이트된 위치에 파트 그리기
            self.image.blit(part_copy, (int(self.part_positions[i][0]), 
                                    int(self.part_positions[i][1])))

    def update_phase_change_animation(self):
        """페이즈 전환 애니메이션 업데이트 - 카메라 고려"""
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time
        self.elapsed_time += dt
        if self.elapsed_time >= self.duration:
            self.kill()
            return

        # Get current camera offset
        camera_offset = self.camera_offset

        # Calculate screen center in world coordinates
        world_center_x = camera_offset.x + (WIDTH // 2)
        scaled_width = self.original_width // 5  # Account for the scale we applied to the image

        phase_duration = (self.duration - self.center_duration) / 2

        if self.elapsed_time < phase_duration:  # Fade in & move to center
            progress = self.elapsed_time / phase_duration
            self.alpha = int(255 * progress)
            
            # Calculate position relative to camera
            start_x = camera_offset.x - scaled_width
            target_x = world_center_x - (scaled_width // 2)
            self.true_pos.x = start_x + (target_x - start_x) * progress
            self.true_pos.y = camera_offset.y + (HEIGHT // 2)
            
        elif self.elapsed_time < phase_duration + self.center_duration:  # Stay in center
            self.alpha = 255
            self.true_pos.x = world_center_x - (scaled_width // 2)
            self.true_pos.y = camera_offset.y + (HEIGHT // 2)
            
        else:  # Fade out & move right
            progress = (self.elapsed_time - (phase_duration + self.center_duration)) / phase_duration
            self.alpha = int(255 * (1 - progress))
            
            start_x = world_center_x - (scaled_width // 2)
            target_x = camera_offset.x + WIDTH
            self.true_pos.x = start_x + (target_x - start_x) * progress
            self.true_pos.y = camera_offset.y + (HEIGHT // 2)

        # Update image alpha
        self.image.set_alpha(self.alpha)
        
        # Update rect position
        self.rect.midleft = self.true_pos

    def update_stat_change_animation(self):
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time
        
        self.elapsed_time += dt
        if self.elapsed_time >= self.duration:
            self.kill()
            return

        # 위로 천천히 이동
        self.rect.y = self.start_y - (self.rise_speed * self.elapsed_time)
        
        # 페이드 인/아웃
        if self.elapsed_time < self.fade_in:
            alpha = int(255 * (self.elapsed_time / self.fade_in))
        elif self.elapsed_time > self.duration - self.fade_out:
            alpha = int(255 * (1 - (self.elapsed_time - (self.duration - self.fade_out)) / self.fade_out))
        else:
            alpha = 255
        
        self.image.set_alpha(alpha)

    def update_level_up_animation(self):
        """레벨업 애니메이션 업데이트"""
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time
        
        self.elapsed_time += dt
        if self.elapsed_time >= self.duration:
            self.kill()
            return

        # 위로 천천히 이동 (처음엔 빠르게, 나중엔 천천히)
        progress = self.elapsed_time / self.duration
        rise_progress = 1 - (1 - progress) * (1 - progress)  # ease-out 효과
        self.rect.centery = self.start_y - (self.rise_height * rise_progress)
        
        # 페이드 인/아웃
        if self.elapsed_time < self.fade_in:
            alpha = int(255 * (self.elapsed_time / self.fade_in))
        elif self.elapsed_time > self.duration - self.fade_out:
            alpha = int(255 * (1 - (self.elapsed_time - (self.duration - self.fade_out)) / self.fade_out))
        else:
            alpha = 255
        
        # 이미지 업데이트
        self.image.fill((0, 0, 0, 0))
        
        # 글로우 효과
        glow_copy = self.glow_surface.copy()
        glow_copy.set_alpha(int(alpha * 0.6))
        glow_rect = glow_copy.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))
        self.image.blit(glow_copy, glow_rect)
        
        # 메인 텍스트
        text_copy = self.text_surface.copy()
        text_copy.set_alpha(alpha)
        text_rect = text_copy.get_rect(center=(self.image.get_width() // 2, self.image.get_height() // 2))
        self.image.blit(text_copy, text_rect)

    def set_position(self, start_pos):
        """애니메이션 위치 설정"""
        if isinstance(start_pos, tuple):
            if self.anchor == 'center':
                self.rect.center = start_pos
            elif self.anchor == 'topleft':
                self.rect.topleft = start_pos
        else:
            if self.anchor == 'center':
                self.rect.center = start_pos.rect.center
            elif self.anchor == 'topleft':
                self.rect.topleft = start_pos.rect.topleft

class AnimationManager:
    def __init__(self, visible_sprites, parent):
        self.visible_sprites = visible_sprites
        self.parent = parent
        self.active_animations = []

    def clear_active_animations(self):
        """현재 활성화된 모든 애니메이션 제거"""
        for anim in self.active_animations:
            if anim.alive():
                anim.kill()
        self.active_animations.clear()

    def has_active_animations(self):
        """현재 실행 중인 애니메이션이 있는지 확인"""
        self.active_animations = [anim for anim in self.active_animations if anim.alive()]
        return len(self.active_animations) > 0

    def create_animation(self, target, animation_type, wait=False, value=None, track_target=False):
        """애니메이션 생성"""
        animation = Animation(target, animation_type, value,track_target=track_target)
        self.visible_sprites.add(animation)

        if wait:
            self.active_animations.append(animation)
        return animation

    def update(self):
        """애니메이션 상태 업데이트"""
        self.active_animations = [anim for anim in self.active_animations if anim.alive()]
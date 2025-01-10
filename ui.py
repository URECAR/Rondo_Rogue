# ui.py
import pygame
from properties import *
from database import *
from support import InputManager, SoundManager
import math
class UI():
    def __init__(self,level):
        self.level = level
        self.display_surface = pygame.display.get_surface()
        self.visible_sprites = level.visible_sprites
        self.font = pygame.font.Font(UI_FONT,16)
        self.input_manager = InputManager()
        self.sound_manager = SoundManager()
        self.cursorUI_rect_width = 50
        self.cursorUI_rect_height = 30

        self.hp_bar_height = 8
        self.hp_bar_width = 48
        
        self.description_scroll_time = 0  # 스크롤 타이밍 추적
        self.description_scroll_speed = 2  # 스크롤 속도 (픽셀/프레임)
        self.description_scroll_pause = 1000  # 스크롤 시작 전 대기 시간 (ms)
        self.last_skill_change = 0  # 마지막 스킬 변경 시간

        self.previous_main_menu = ''
        self.neutral_main_menu = ''
        self.current_main_menu = ''
        self.selected_menu = 'init'
        self.current_skill_menu_index = 0
        self.current_item_menu_index = 0
        
        self.info_tab = 'items'  # 'items', 'skills', 'profile'
        self.info_item_index = 0  # 아이템 선택 인덱스
        self.info_equip_index = 0  # 장비 선택 인덱스
        self.info_skill_index = 0  # 스킬 선택 인덱스
        self.in_equip_section = False  # 아이템/장비 영역 구분
        
        self.status_rotation_time = 2000  # 2초마다 변경
        self.last_status_change = 0       # 마지막 변경 시간
        self.current_status_index = 0     # 현재 표시 중인 상태이상 인덱스

    def show_cursorUI(self):
        cursor_x = self.level.cursor.rect.topleft[0] // TILESIZE
        cursor_y = self.level.cursor.rect.topleft[1] // TILESIZE
        if self.level.cursor.level.level_data['moves'][cursor_x][cursor_y] == '-1':
            text = self.font.render(f"이동 불가", True, TEXT_COLOR)
        else:
            text = self.font.render(f"move: {self.level.cursor.level.level_data['moves'][cursor_x][cursor_y]}", True, TEXT_COLOR)
        text_rect = text.get_rect()
        text_rect.bottomleft = self.level.cursor.rect.topright - self.visible_sprites.offset
        self.display_surface.blit(text,text_rect)

    def show_Moves(self):
        selected_battler = self.level.map_action.selected_battler
        if selected_battler:
            text = self.font.render(f"Move: {self.level.map_action.cur_moves}/{selected_battler.stats['Mov']}", True, TEXT_COLOR)
            text_rect = text.get_rect()
            text_rect.bottomleft = self.level.cursor.rect.topright - self.visible_sprites.offset
            self.display_surface.blit(text,text_rect)
# UI 클래스 내에서
    def show_characterUI(self, character):
        char_data = CharacterDatabase.data.get(character.char_type, {})
        hidden_stats = char_data.get('hidden_stats', [])

        # 패널 크기 및 위치 계산
        CHARACTER_PANEL_WIDTH = 220
        level_section_width = 70  # Lv 섹션의 너비
        name_section_width = CHARACTER_PANEL_WIDTH - level_section_width
        header_height = 15
        exp_height = 25
        status_height = 25
        divider_margin = 5
        bar_height = 10
        bar_section_height = 150
        stats_height = 85
        total_panel_height = header_height + divider_margin + status_height + bar_section_height + stats_height

        # 화면 기준 배틀러의 상대적 위치 계산
        screen_width = self.display_surface.get_width()
        battler_screen_x = character.rect.centerx - self.visible_sprites.offset.x

        # 패널 위치 결정 (왼쪽/오른쪽)
        if battler_screen_x > screen_width / 2:
            panel_x = character.rect.left - self.visible_sprites.offset.x - CHARACTER_PANEL_WIDTH - MENU_OFFSET
        else:
            panel_x = character.rect.right - self.visible_sprites.offset.x + MENU_OFFSET

        panel_y = character.rect.top - self.visible_sprites.offset.y

        # 패널이 화면 영역을 벗어나지 않도록 조정
        if panel_y < 0:
            panel_y = 0
        if panel_y + total_panel_height > self.display_surface.get_height():
            panel_y = self.display_surface.get_height() - total_panel_height

        # 패널 그리기
        panel_rect = pygame.Rect(panel_x, panel_y, CHARACTER_PANEL_WIDTH, total_panel_height)
        bg_surface = pygame.Surface((CHARACTER_PANEL_WIDTH, total_panel_height), pygame.SRCALPHA)
        bg_color = (*UI_BG_COLOR, PANEL_ALPHA)
        pygame.draw.rect(bg_surface, bg_color, bg_surface.get_rect(), border_radius=PANEL_BORDER_RADIUS)
        self.display_surface.blit(bg_surface, panel_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, panel_rect, 2, border_radius=PANEL_BORDER_RADIUS)

        current_y = panel_y + 10

        # 1. 이름과 레벨 표시
        name_color = ENERGY_COLOR if character.team == 'Ally' else (255, 100, 100)
        name_font = pygame.font.Font(UI_FONT, 18)
        name_text = name_font.render(character.name, True, name_color)
        name_rect = name_text.get_rect(topleft=(panel_x + 15, current_y))
        self.display_surface.blit(name_text, name_rect)

        # Lv 표시
        level_section_x = panel_x + name_section_width
        level_font = pygame.font.Font(UI_FONT, 16)
        lv_text = level_font.render("Lv.", True, (255, 255, 200))
        level_number = level_font.render(str(character.LV), True, (255, 255, 200))
        
        lv_rect = lv_text.get_rect(topleft=(level_section_x + 10, current_y + 3))
        level_rect = level_number.get_rect(midleft=(lv_rect.right + 5, lv_rect.centery))
        
        self.display_surface.blit(lv_text, lv_rect)
        self.display_surface.blit(level_number, level_rect)

        # EXP 바
        exp_ratio = character.exp / character.stats['Max_EXP']
        exp_bar_width = level_section_width + 30
        exp_bar_height = 12
        
        exp_font = pygame.font.Font(UI_FONT, 12)
        exp_text = exp_font.render(f"{int(character.exp)} / {character.stats['Max_EXP']}", True, EXP_COLOR)
        exp_text_rect = exp_text.get_rect(topleft=(level_section_x - 10, current_y + 35))
        self.display_surface.blit(exp_text, exp_text_rect)

        exp_bar_rect = pygame.Rect(level_section_x - 50, current_y + 50, exp_bar_width, exp_bar_height)
        pygame.draw.rect(self.display_surface, (60, 60, 60), exp_bar_rect, border_radius=3)
        
        exp_fill_rect = pygame.Rect(level_section_x - 50, current_y + 50, 
                                int(exp_bar_width * exp_ratio), exp_bar_height)
        pygame.draw.rect(self.display_surface, EXP_COLOR, exp_fill_rect, border_radius=3)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, exp_bar_rect, 1, border_radius=3)

        # 2. 상태 표시
        current_y += header_height + exp_height
        status_font = pygame.font.Font(UI_FONT, 16)
        
        # 상태이상 효과 필터링 - 동일한 기본 상태이상은 하나로 취급
        unique_status_effects = {}
        for effect in character.effects:
            if effect.type == 'status':
                # percent나 flat 등의 suffix 제거
                base_status = effect.source.replace('status_', '').split('_')[0]
                unique_status_effects[base_status] = effect

        status_effects = list(unique_status_effects.values())
        
        if status_effects:
            # 2초마다 표시할 상태이상 변경
            current_time = pygame.time.get_ticks()
            if current_time - self.last_status_change >= self.status_rotation_time:
                self.last_status_change = current_time
                self.current_status_index = (self.current_status_index + 1) % len(status_effects)

            # 현재 표시할 상태이상 선택
            current_status = status_effects[self.current_status_index]
            status_text = current_status.source.replace('status_', '').split('_')[0]
            status_color = (255, 255, 100)  # 노란색
        else:
            if character.inactive:
                status_text = "쉬는 중"
                status_color = (150, 150, 150)  # 회색
            else:
                status_text = "멀쩡함"
                status_color = (100, 255, 100)  # 초록색
                self.current_status_index = 0

        status_surface = status_font.render(status_text, True, status_color)
        status_rect = status_surface.get_rect(topleft=(panel_x + 15, current_y))
        self.display_surface.blit(status_surface, status_rect)


        # 3. HP, MP 바
        current_y += status_height + 30
        bar_width = CHARACTER_PANEL_WIDTH - 30
        bar_spacing = 40
        bar_height = 12

        # HP 바
        hp_ratio = character.Cur_HP / character.stats['Max_HP']
        self.draw_stat_bar(panel_x + 15, current_y, bar_width, bar_height, 
                          "HP", hp_ratio, 
                          f"{int(character.Cur_HP)}/{int(character.stats['Max_HP'])}", 
                          HEALTH_COLOR)
        
        # MP 바
        current_y += bar_spacing
        mp_ratio = character.Cur_MP / character.stats['Max_MP']
        self.draw_stat_bar(panel_x + 15, current_y, bar_width, bar_height, 
                          "MP", mp_ratio, 
                          f"{int(character.Cur_MP)}/{int(character.stats['Max_MP'])}", 
                          ENERGY_COLOR)

        # 4. 스탯 표시
        current_y += 25
        stat_pairs = [('STR', 'DEX'), ('INT', 'RES'), ('Mov', 'CHA')]
        stat_font = pygame.font.Font(UI_FONT, 16)

        for i, (left_stat, right_stat) in enumerate(stat_pairs):
            y_pos = current_y + i * 30
            self.draw_stat_value(panel_x + 20, y_pos, left_stat, character, hidden_stats, stat_font)
            self.draw_stat_value(panel_x + 120, y_pos, right_stat, character, hidden_stats, stat_font)

    def draw_stat_bar(self, x, y, width, height, label, ratio, value_text, color):
            font = pygame.font.Font(UI_FONT, 18)
            current_val, max_val = value_text.split('/')

            # 텍스트 렌더링
            label_surface = font.render(label, True, color)
            label_rect = label_surface.get_rect(bottomleft=(x, y - 2))
            self.display_surface.blit(label_surface, label_rect)

            current_surface = font.render(str(current_val).rjust(4), True, TEXT_COLOR)
            current_rect = current_surface.get_rect(bottomleft=(x + 50, y - 2))
            self.display_surface.blit(current_surface, current_rect)

            separator_surface = font.render("/", True, TEXT_COLOR)
            separator_rect = separator_surface.get_rect(bottomleft=(current_rect.right + 5, y - 2))
            self.display_surface.blit(separator_surface, separator_rect)

            max_surface = font.render(str(max_val).ljust(4), True, TEXT_COLOR)
            max_rect = max_surface.get_rect(bottomleft=(separator_rect.right + 5, y - 2))
            self.display_surface.blit(max_surface, max_rect)

            # 바 그리기
            bg_rect = pygame.Rect(x, y, width, height)
            pygame.draw.rect(self.display_surface, (60, 60, 60), bg_rect, border_radius=5)
            
            bar_width = int(width * ratio)
            bar_rect = pygame.Rect(x, y, bar_width, height)
            pygame.draw.rect(self.display_surface, color, bar_rect, border_radius=5)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, bg_rect, 1, border_radius=5)

    def draw_stat_value(self, x, y, stat, character, hidden_stats, font):
        """개별 스탯 값 표시"""
        diff_font = pygame.font.Font(UI_FONT, 10)
        
        # 숨겨진 스탯 처리
        if stat in hidden_stats:
            value = "???"
            stat_color = value_color = (255, 100, 100)
        else:
            value = str(int(character.stats[stat]))
            stat_color = TEXT_COLOR
            
            # 기본값과 현재값의 차이 계산
            base_value = int(character.base_stats.get(stat, 0))
            current_value = int(character.stats[stat])
            value_color = (TEXT_COLOR if current_value == base_value else 
                        (150, 255, 150) if current_value > base_value else 
                        (255, 150, 150))

        # 스탯 이름 표시
        name_text = f"{stat}: "
        name_surface = font.render(name_text, True, stat_color)
        self.display_surface.blit(name_surface, (x, y))

        # 스탯 값 표시
        value_surface = font.render(value, True, value_color)
        value_rect = value_surface.get_rect(topleft=(x + name_surface.get_width(), y))
        self.display_surface.blit(value_surface, value_rect)

        # 차이값 표시 (숨겨진 스탯이 아닐 경우)
        if stat not in hidden_stats:
            stat_diff = int(character.stats[stat]) - int(character.base_stats[stat])
            if stat_diff != 0:
                diff_color = (150, 255, 150) if stat_diff > 0 else (255, 150, 150)
                diff_text = f"({'+' if stat_diff > 0 else ''}{stat_diff})"
                diff_surface = diff_font.render(diff_text, True, diff_color)
                diff_rect = diff_surface.get_rect(topleft=(value_rect.right + 5, y + 2))
                self.display_surface.blit(diff_surface, diff_rect)

    def show_player_menu(self, current_menu):
        if not current_menu or not self.level.map_action.selected_battler:
            return

        selected_battler = self.level.map_action.selected_battler
        
        # 화면 기준 배틀러의 상대적 x 위치 계산
        screen_width = self.display_surface.get_width()
        battler_screen_x = selected_battler.rect.centerx - self.visible_sprites.offset.x

        # 배틀러가 화면의 왼쪽 절반에 있는지 확인
        is_on_left = battler_screen_x < screen_width / 2

        # 메뉴 아이템 구성
        menu_items = []
        menu_actions = []
        
        # Range 타입 캐릭터인 경우 '사격' 메뉴 추가
        char_data = CharacterDatabase.data.get(selected_battler.char_type, {})
        if char_data.get('Class') == 'Range' and not selected_battler.inactive:
            menu_items.append('사격')
            menu_actions.append('range')
        active_skills = [skill for skill in selected_battler.skills 
            if SKILL_PROPERTIES[skill]['Type'] == 'Active']
        if active_skills and not selected_battler.inactive:
            menu_items.append('스킬')
            menu_actions.append('skill')
        if selected_battler.inventory and not selected_battler.inactive:
            menu_items.append('아이템')
            menu_actions.append('item')
            
        menu_items.extend(['정보'])
        menu_actions.extend(['info'])
        
        # 기본 메뉴 항목 추가
        if not selected_battler.inactive:
            menu_items.extend(['대기'])
            menu_actions.extend(['wait'])
        

        if is_on_left:
            # 배틀러가 왼쪽에 있으면 메뉴는 오른쪽에
            base_x = selected_battler.rect.right - self.visible_sprites.offset.x + MENU_OFFSET
        else:
            # 배틀러가 오른쪽에 있으면 메뉴는 왼쪽에
            base_x = selected_battler.rect.left - self.visible_sprites.offset.x - MENU_PANEL_WIDTH - MENU_OFFSET
        base_y = selected_battler.rect.centery - self.visible_sprites.offset.y - (len(menu_items) * MENU_PANEL_HEIGHT + MENU_PANEL_SPACING)

        mouse_pos = self.input_manager.mouse_pos

        for i, (item, action) in enumerate(zip(menu_items, menu_actions)):
            menu_rect = pygame.Rect(
                base_x,
                base_y + i * (MENU_PANEL_HEIGHT + MENU_PANEL_SPACING),
                MENU_PANEL_WIDTH,
                MENU_PANEL_HEIGHT
            )

            # 선택된 메뉴 항목 강조
            is_selected = (self.selected_menu == action)
            is_hovered = menu_rect.collidepoint(mouse_pos)
            
            # 배경색 결정 (선택됨 > 호버 > 기본)
            if is_selected:
                bg_color = UPGRADE_BG_COLOR_SELECTED
                border_color = UI_BORDER_COLOR_ACTIVE
            elif is_hovered:
                bg_color = (80, 80, 80)
                border_color = UI_BORDER_COLOR
            else:
                bg_color = UI_BG_COLOR
                border_color = UI_BORDER_COLOR
            # 배경색 설정
            pygame.draw.rect(self.display_surface, bg_color, menu_rect, border_radius=PANEL_BORDER_RADIUS)            
            # 테두리 색상 설정
            pygame.draw.rect(self.display_surface, border_color, menu_rect, 2, border_radius=PANEL_BORDER_RADIUS)

            text = self.font.render(item, True, TEXT_COLOR_SELECTED if is_selected else TEXT_COLOR)
            text_rect = text.get_rect(center=menu_rect.center)
            self.display_surface.blit(text, text_rect)
    # 스킬 창
    def show_skill_menu(self, selected_skill_index):
        """스킬 선택 메뉴 표시"""
        if self.current_main_menu != self.previous_main_menu:
            return

        selected_battler = self.level.map_action.selected_battler
        active_skills = [skill for skill in selected_battler.skills 
                        if SKILL_PROPERTIES[skill]['Type'] == 'Active']
        
        if not active_skills:
            return

        # 기본 메뉴 크기 계산
        skill_menu_width = MENU_PANEL_WIDTH * 2.5
        description_height = MENU_PANEL_HEIGHT * 1.5  # 설명란 높이
        skills_start_y = MENU_PANEL_HEIGHT * 2 # 스킬 목록 시작 위치
        visible_skills = 4  # 한 번에 보여줄 스킬 수
        skill_menu_height = skills_start_y + (MENU_PANEL_HEIGHT + 16) * visible_skills

        # 메뉴 위치 계산
        screen_width = self.display_surface.get_width()
        battler_screen_x = selected_battler.rect.centerx - self.visible_sprites.offset.x
        is_on_left = battler_screen_x < screen_width / 2

        if is_on_left:
            base_x = selected_battler.rect.right - self.visible_sprites.offset.x + MENU_OFFSET
        else:
            base_x = selected_battler.rect.left - self.visible_sprites.offset.x - skill_menu_width - MENU_OFFSET

        base_y = selected_battler.rect.centery - self.visible_sprites.offset.y - skill_menu_height // 2

        # 메인 패널
        menu_rect = pygame.Rect(base_x, base_y, skill_menu_width, skill_menu_height)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, menu_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, menu_rect, 2)

        # 스크롤 위치 계산
        max_skills = len(active_skills)
        scroll_offset = max(0, min(selected_skill_index - (visible_skills - 2), max_skills - visible_skills))
        visible_skills_list = active_skills[scroll_offset:scroll_offset + visible_skills]

        # 화살표 애니메이션
        current_time = pygame.time.get_ticks()
        arrow_offset = abs(math.sin(current_time / 300)) * 5
        arrow_size = 12
        arrow_color = UI_BORDER_COLOR

        selected_skill = active_skills[selected_skill_index]
        skill_info = SKILL_PROPERTIES[selected_skill]
        skill_level = selected_battler.skills[selected_skill]

        # 설명 텍스트 포맷팅
        description = skill_info['Description'].strip()
        format_dict = {}
        
        for key, value in skill_info.items():
            if isinstance(value, dict) and skill_level in value:
                if isinstance(value[skill_level], dict):
                    format_dict.update(value[skill_level])
                else:
                    format_dict[key] = value[skill_level]
        
        try:
            description = description.format(**format_dict)
        except KeyError:
            pass

        # 설명 텍스트 영역
        description_rect = pygame.Rect(
            base_x + 10,
            base_y + 10,
            skill_menu_width - 20,
            description_height
        )
        pygame.draw.rect(self.display_surface, (UI_BG_COLOR[0]-20, UI_BG_COLOR[1]-20, UI_BG_COLOR[2]-20), 
                        description_rect, border_radius=5)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, description_rect, 1, border_radius=5)

        # 설명 텍스트 줄바꿈 및 표시
        description_lines = self.wrap_text(description, self.font, skill_menu_width - 40)
        if len(description_lines) > 2:
            # 스킬 변경 시 스크롤 초기화
            current_time = pygame.time.get_ticks()
            if self.current_skill_menu_index != getattr(self, 'last_skill_index', None):
                self.description_scroll_time = current_time
                self.last_skill_index = self.current_skill_menu_index
            
            # 스크롤 위치 계산
            if current_time - self.description_scroll_time > self.description_scroll_pause:
                scroll_offset = ((current_time - self.description_scroll_time - self.description_scroll_pause) 
                            // self.description_scroll_speed % (len(description_lines) * 20))
            else:
                scroll_offset = 0

            # 보이는 줄 계산
            visible_lines = []
            total_height = 0
            for line in description_lines:
                line_height = self.font.get_size()[1]
                if total_height - scroll_offset < 40:  # 최대 2줄까지
                    visible_lines.append(line)
                total_height += line_height

            # 보이는 줄 표시
            for i, line in enumerate(visible_lines):
                line_surface = self.font.render(line, True, TEXT_COLOR)
                line_rect = line_surface.get_rect(
                    topleft=(base_x + 20, base_y + 20 + i * 20)
                )
                self.display_surface.blit(line_surface, line_rect)
        else:
            # 2줄 이하면 그냥 표시
            for i, line in enumerate(description_lines):
                line_surface = self.font.render(line, True, TEXT_COLOR)
                line_rect = line_surface.get_rect(
                    topleft=(base_x + 20, base_y + 20 + i * 20)
                )
                self.display_surface.blit(line_surface, line_rect)

        # 구분선과 장식 추가
        separator_y = base_y + skills_start_y - 10
        pygame.draw.line(
            self.display_surface,
            UI_BORDER_COLOR,
            (base_x + 20, separator_y),
            (base_x + skill_menu_width - 20, separator_y),
            2
        )
        
        # 장식용 구분점 추가
        dot_radius = 3
        dot_x = base_x + skill_menu_width // 2
        pygame.draw.circle(self.display_surface, UI_BORDER_COLOR, (dot_x, separator_y), dot_radius)
        pygame.draw.circle(self.display_surface, UI_BORDER_COLOR, (dot_x - 15, separator_y), dot_radius-1)
        pygame.draw.circle(self.display_surface, UI_BORDER_COLOR, (dot_x + 15, separator_y), dot_radius-1)

        # 스크롤 화살표 표시
        if scroll_offset > 0:  # 위쪽 화살표
            arrow_y = base_y + skills_start_y - 5  # 위쪽 화살표 위치
            points_up = [
                (menu_rect.centerx - arrow_size // 2, arrow_y + arrow_size - arrow_offset),
                (menu_rect.centerx + arrow_size // 2, arrow_y + arrow_size - arrow_offset),
                (menu_rect.centerx, arrow_y - arrow_offset)
            ]
            pygame.draw.polygon(self.display_surface, arrow_color, points_up)

        if scroll_offset + visible_skills < max_skills:  # 아래쪽 화살표
            arrow_y = menu_rect.bottom - 20  # 아래쪽 화살표 위치
            points_down = [
                (menu_rect.centerx - arrow_size // 2, arrow_y + arrow_offset),
                (menu_rect.centerx + arrow_size // 2, arrow_y + arrow_offset),
                (menu_rect.centerx, arrow_y + arrow_size + arrow_offset)
            ]
            pygame.draw.polygon(self.display_surface, arrow_color, points_down)

        mouse_pos = pygame.mouse.get_pos()

        # 스킬 목록 표시
        for i, skill in enumerate(visible_skills_list):
            skill_info = SKILL_PROPERTIES[skill]
            skill_level = selected_battler.skills[skill]
            
            # 마나 체크
            mana_cost = skill_info.get('Mana', {}).get(skill_level, 0)
            has_enough_mana = selected_battler.Cur_MP >= mana_cost
            
            # 스킬 항목 배경
            item_rect = pygame.Rect(
                base_x + 10,
                base_y + skills_start_y + 10 + i * (MENU_PANEL_HEIGHT + 10),
                skill_menu_width - 20,
                MENU_PANEL_HEIGHT
            )

            # 스타일 적용
            style_name = skill_info.get('Style', 'default')
            style = SKILL_STYLES[style_name]
            
            is_selected = (i + scroll_offset == selected_skill_index)
            is_hovered = item_rect.collidepoint(mouse_pos)
            
            # 배경색 결정
            if is_selected:
                bg_color = UPGRADE_BG_COLOR_SELECTED
                border_color = style['border_color']
                text_color = style['text_color'] if has_enough_mana else (100, 100, 100)
            elif is_hovered:
                bg_color = (80, 80, 80)
                border_color = style['border_color']
                text_color = style['text_color'] if has_enough_mana else (100, 100, 100)
            else:
                bg_color = (UI_BG_COLOR[0]-10, UI_BG_COLOR[1]-10, UI_BG_COLOR[2]-10)
                border_color = style['border_color']
                text_color = style['text_color'] if has_enough_mana else (100, 100, 100)

            # 배경 그리기
            pygame.draw.rect(self.display_surface, bg_color, item_rect, border_radius=5)
            pygame.draw.rect(self.display_surface, border_color, item_rect, 1, border_radius=5)

            # 스킬 이름과 마나 비용을 별도의 Surface에 렌더링
            text_surface = pygame.Surface((skill_menu_width - 20, MENU_PANEL_HEIGHT), pygame.SRCALPHA)

            # 스킬 이름 렌더링
            name_text = self.font.render(skill, True, text_color)
            name_rect = name_text.get_rect(midleft=(10, MENU_PANEL_HEIGHT // 2))
            text_surface.blit(name_text, name_rect)

            # 마나 비용 표시
            if 'Mana' in skill_info:
                mana_cost = f"MP {mana_cost}"
                mana_text = self.font.render(mana_cost, True, text_color)
                mana_rect = mana_text.get_rect(midright=(skill_menu_width - 30, MENU_PANEL_HEIGHT // 2))
                text_surface.blit(mana_text, mana_rect)

            # text_surface를 메인 화면에 blit
            self.display_surface.blit(text_surface, item_rect)

    def show_item_menu(self, selected_item_index):
        """스킬 / 아이템 / 기타 메뉴 중에서 '아이템' 메뉴를 열었을 때의 표시 로직"""
        # 만약 메인메뉴(current_main_menu)가 갓 바뀐 상황이 아니라면, 표시하지 않음
        if self.current_main_menu != self.previous_main_menu:
            return
        
        selected_battler = self.level.map_action.selected_battler
        if not selected_battler:
            return
        
        # 메뉴 크기 계산
        item_menu_width = MENU_PANEL_WIDTH * 2.5
        description_height = MENU_PANEL_HEIGHT * 1.5  # 설명란 높이
        items_start_y = MENU_PANEL_HEIGHT * 2  # 아이템 목록 시작 위치
        items_display_count = min(4, len(selected_battler.inventory))
        item_menu_height = items_start_y + (MENU_PANEL_HEIGHT + 10) * items_display_count

        # 배틀러가 화면의 왼쪽/오른쪽 어느 쪽에 있는지 판단해서 메뉴 위치 결정
        screen_width = self.display_surface.get_width()
        battler_screen_x = selected_battler.rect.centerx - self.visible_sprites.offset.x
        is_on_left = battler_screen_x < screen_width / 2

        if is_on_left:
            base_x = selected_battler.rect.right - self.visible_sprites.offset.x + MENU_OFFSET
        else:
            base_x = selected_battler.rect.left - self.visible_sprites.offset.x - item_menu_width - MENU_OFFSET

        base_y = selected_battler.rect.centery - self.visible_sprites.offset.y - item_menu_height // 2

        # 메인 패널(배경 사각형) 그리기
        menu_rect = pygame.Rect(base_x, base_y, item_menu_width, item_menu_height)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, menu_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, menu_rect, 2)

        # 아이템이 존재할 경우에만 설명 영역 및 구분선 등을 그려줌
        if selected_battler.inventory:
            # 현재 선택된 아이템
            selected_item = selected_battler.inventory[selected_item_index]
            item_info = ITEM_PROPERTIES[selected_item]

            # ───── 설명란 ─────
            description_rect = pygame.Rect(
                base_x + 10,
                base_y + 10,
                item_menu_width - 20,
                description_height
            )
            pygame.draw.rect(
                self.display_surface, 
                (UI_BG_COLOR[0] - 20, UI_BG_COLOR[1] - 20, UI_BG_COLOR[2] - 20), 
                description_rect, 
                border_radius=5
            )
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, description_rect, 1, border_radius=5)

            # 설명 텍스트 표시 (최대 2줄)
            description_lines = self.wrap_text(item_info['Description'], self.font, item_menu_width - 40)
            for i, line in enumerate(description_lines[:2]):
                line_surface = self.font.render(line, True, TEXT_COLOR)
                line_rect = line_surface.get_rect(topleft=(base_x + 20, base_y + 20 + i * 20))
                self.display_surface.blit(line_surface, line_rect)

            # ───── 구분선 및 장식점 ─────
            separator_y = base_y + items_start_y - 10
            pygame.draw.line(
                self.display_surface,
                UI_BORDER_COLOR,
                (base_x + 20, separator_y),
                (base_x + item_menu_width - 20, separator_y),
                2
            )

            # 장식용 구분점
            dot_radius = 3
            dot_x = base_x + item_menu_width // 2
            pygame.draw.circle(self.display_surface, UI_BORDER_COLOR, (dot_x, separator_y), dot_radius)
            pygame.draw.circle(self.display_surface, UI_BORDER_COLOR, (dot_x - 15, separator_y), dot_radius - 1)
            pygame.draw.circle(self.display_surface, UI_BORDER_COLOR, (dot_x + 15, separator_y), dot_radius - 1)

            # ───── 아이템 목록 표시 ─────
            mouse_pos = pygame.mouse.get_pos()
            
            # 아이콘 관련 설정
            icon_size = 24       # 아이콘 가로/세로 크기
            icon_padding = 5     # item_rect 안에서 아이콘을 띄울 여백
            name_padding = 10    # 아이콘과 글자 사이 간격

            for i, item in enumerate(selected_battler.inventory[:items_display_count]):
                item_info = ITEM_PROPERTIES[item]

                # 각 아이템 메뉴 패널의 위치/크기
                item_rect = pygame.Rect(
                    base_x + 10,
                    base_y + items_start_y + i * (MENU_PANEL_HEIGHT + 10),
                    item_menu_width - 20,
                    MENU_PANEL_HEIGHT
                )

                # 선택 여부 / 마우스 호버 여부
                is_selected = (i == selected_item_index)
                is_hovered = item_rect.collidepoint(mouse_pos)

                # 배경/테두리/글자 색상 결정
                if is_selected:
                    bg_color = UPGRADE_BG_COLOR_SELECTED
                    border_color = UI_BORDER_COLOR_ACTIVE
                    text_color = TEXT_COLOR_SELECTED
                elif is_hovered:
                    bg_color = (80, 80, 80)
                    border_color = UI_BORDER_COLOR
                    text_color = TEXT_COLOR
                else:
                    bg_color = (UI_BG_COLOR[0] - 10, UI_BG_COLOR[1] - 10, UI_BG_COLOR[2] - 10)
                    border_color = UI_BORDER_COLOR
                    text_color = TEXT_COLOR

                # 배경 그리기
                pygame.draw.rect(self.display_surface, bg_color, item_rect, border_radius=5)
                pygame.draw.rect(self.display_surface, border_color, item_rect, 1, border_radius=5)

                # ── [아이콘 표시] ──
                icon_x = item_rect.x + icon_padding
                icon_y = item_rect.centery - icon_size // 2
                if 'icon_path' in item_info:
                    try:
                        icon_surf = pygame.image.load(item_info['icon_path']).convert_alpha()
                        icon_surf = pygame.transform.scale(icon_surf, (icon_size, icon_size))
                        self.display_surface.blit(icon_surf, (icon_x, icon_y))
                    except:
                        print(f"아이콘 로드 실패: {item_info['icon_path']}")
                        # 로드 실패 시, 대체 처리를 원한다면 여기에 작성(기본 아이콘 등)

                # ── [아이템 이름 표시] ──
                name_text = self.font.render(item_info['name'], True, text_color)
                name_rect = name_text.get_rect(
                    midleft=(icon_x + icon_size + name_padding, item_rect.centery)
                )
                self.display_surface.blit(name_text, name_rect)

    def show_info_menu(self):
        """정보 UI 표시"""
        selected_battler = self.level.map_action.selected_battler
        if not selected_battler:
            return
                
        # 메뉴 크기 확장
        menu_width = MENU_PANEL_WIDTH * 3  # 더 넓게
        menu_height = MENU_PANEL_HEIGHT * 10  # 더 길게
        
        # 화면 기준 배틀러의 상대적 위치 계산
        screen_width = self.display_surface.get_width()
        battler_screen_x = selected_battler.rect.centerx - self.visible_sprites.offset.x
        is_on_left = battler_screen_x < screen_width / 2
        
        if is_on_left:
            base_x = selected_battler.rect.right - self.visible_sprites.offset.x + MENU_OFFSET
        else:
            base_x = selected_battler.rect.left - self.visible_sprites.offset.x - menu_width - MENU_OFFSET
        base_y = selected_battler.rect.centery - self.visible_sprites.offset.y - menu_height // 2
        
        # 메인 패널 그리기
        menu_rect = pygame.Rect(base_x, base_y, menu_width, menu_height)
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, menu_rect)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, menu_rect, 2)
        
        # 마우스 위치 확인
        mouse_pos = pygame.mouse.get_pos()
        
        # 탭 그리기
        tab_width = menu_width // 3
        tab_height = 30
        tabs = [('인벤토리', 'items'), ('스킬', 'skills'), ('정보', 'profile')]
        
        for i, (tab_name, tab_id) in enumerate(tabs):
            tab_rect = pygame.Rect(base_x + i * tab_width, base_y, tab_width, tab_height)
            is_selected = self.info_tab == tab_id
            is_hovered = tab_rect.collidepoint(mouse_pos)
            
            # 배경색 결정 (선택됨 > 호버 > 기본)
            if is_selected:
                bg_color = UPGRADE_BG_COLOR_SELECTED
                text_color = TEXT_COLOR_SELECTED
            elif is_hovered:
                bg_color = (80, 80, 80)
                text_color = TEXT_COLOR
            else:
                bg_color = UI_BG_COLOR
                text_color = TEXT_COLOR
                
            pygame.draw.rect(self.display_surface, bg_color, tab_rect)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, tab_rect, 2)
            
            text = self.font.render(tab_name, True, text_color)
            text_rect = text.get_rect(center=tab_rect.center)
            self.display_surface.blit(text, text_rect)
        
        # 컨텐츠 영역
        content_rect = pygame.Rect(base_x, base_y + tab_height, menu_width, menu_height - tab_height)
        
        if self.info_tab == 'items':
            self.show_items_tab(content_rect, selected_battler)
        elif self.info_tab == 'skills':
            self.show_skills_tab(content_rect, selected_battler)
        elif self.info_tab == 'profile':
            self.show_profile_tab(content_rect, selected_battler)    # 정보 - 아이템 창

    def show_items_tab(self, rect, battler):
        """인벤토리 탭 내용 표시"""
        section_font = pygame.font.Font(UI_FONT, 18)
        normal_font = self.font
        
        padding_x = 15
        padding_y = 15
        column_width = (rect.width // 2) - (padding_x * 2)
        description_x = rect.x + (rect.width // 2) + padding_x
        description_width = (rect.width // 2) - (padding_x * 2)
        
        item_box_height = 28
        item_box_spacing = 4
        items_per_section = 4  # 각 섹션당 고정된 아이템 수
        
        # 아이템 섹션
        items_title_y = rect.y + padding_y
        items_text = section_font.render("아이템", True, TEXT_COLOR)
        self.display_surface.blit(items_text, (rect.x + padding_x, items_title_y))
        
        items_start_y = items_title_y + 30
        fixed_section_height = items_per_section * (item_box_height + item_box_spacing)
        
        # 아이템 목록 표시
        for i in range(items_per_section):
            item_rect = pygame.Rect(
                rect.x + padding_x,
                items_start_y + i * (item_box_height + item_box_spacing),
                column_width,
                item_box_height
            )
            
            # 실제 아이템이 있는 경우만 아이템 정보 표시
            if i < len(battler.inventory):
                item = battler.inventory[i]
                is_selected = (i == self.info_item_index and not self.in_equip_section)
                is_hovered = item_rect.collidepoint(pygame.mouse.get_pos())
                
                # 배경색 결정
                if is_selected:
                    bg_color = UPGRADE_BG_COLOR_SELECTED
                    text_color = TEXT_COLOR_SELECTED
                elif is_hovered:
                    bg_color = (80, 80, 80)
                    text_color = TEXT_COLOR
                else:
                    bg_color = UI_BG_COLOR
                    text_color = TEXT_COLOR
                    
                pygame.draw.rect(self.display_surface, bg_color, item_rect, border_radius=5)
                pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, item_rect, 1, border_radius=5)
                
                text = normal_font.render(ITEM_PROPERTIES[item]['name'], True, text_color)
                self.display_surface.blit(text, (item_rect.x + 8, item_rect.y + (item_box_height - text.get_height())//2))
            else:
                # 빈 슬롯 표시
                pygame.draw.rect(self.display_surface, UI_BG_COLOR, item_rect, border_radius=5)
                pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, item_rect, 1, border_radius=5)

        # 장비 섹션 - 고정된 위치에 표시
        equip_title_y = items_start_y + fixed_section_height + 25
        equip_text = section_font.render("장비", True, TEXT_COLOR)
        self.display_surface.blit(equip_text, (rect.x + padding_x, equip_title_y))
        
        equip_start_y = equip_title_y + 30
        
        # 장비 목록 표시
        for i in range(items_per_section):
            equip_rect = pygame.Rect(
                rect.x + padding_x,
                equip_start_y + i * (item_box_height + item_box_spacing),
                column_width,
                item_box_height
            )
            
            # 실제 장비가 있는 경우만 장비 정보 표시
            if i < len(battler.equips):
                equip = battler.equips[i]
                is_selected = (i == self.info_equip_index and self.in_equip_section)
                is_hovered = equip_rect.collidepoint(pygame.mouse.get_pos())
                
                # 배경색 결정
                if is_selected:
                    bg_color = UPGRADE_BG_COLOR_SELECTED
                    text_color = TEXT_COLOR_SELECTED
                elif is_hovered:
                    bg_color = (80, 80, 80)
                    text_color = TEXT_COLOR
                else:
                    bg_color = UI_BG_COLOR
                    text_color = TEXT_COLOR
                    
                pygame.draw.rect(self.display_surface, bg_color, equip_rect, border_radius=5)
                pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, equip_rect, 1, border_radius=5)
                
                text = normal_font.render(equip, True, text_color)
                self.display_surface.blit(text, (equip_rect.x + 8, equip_rect.y + (item_box_height - text.get_height())//2))
            else:
                # 빈 슬롯 표시
                pygame.draw.rect(self.display_surface, UI_BG_COLOR, equip_rect, border_radius=5)
                pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, equip_rect, 1, border_radius=5)
        
        # 설명란
        description_rect = pygame.Rect(description_x, rect.y + padding_y, description_width, rect.height - padding_y * 2)
        pygame.draw.rect(self.display_surface, (UI_BG_COLOR[0]-20, UI_BG_COLOR[1]-20, UI_BG_COLOR[2]-20), description_rect, border_radius=5)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, description_rect, 1, border_radius=5)
        
        # 선택된 아이템/장비의 설명 표시
        description = ""
        if self.in_equip_section and battler.equips and 0 <= self.info_equip_index < len(battler.equips):
            selected_item = battler.equips[self.info_equip_index]
            description = EQUIP_PROPERTIES[selected_item]['Description']
        elif not self.in_equip_section and battler.inventory and 0 <= self.info_item_index < len(battler.inventory):
            selected_item = battler.inventory[self.info_item_index]
            description = ITEM_PROPERTIES[selected_item]['Description']
        
        description_lines = self.wrap_text(description, normal_font, description_width - 20)
        for i, line in enumerate(description_lines[:10]):
            text_surf = normal_font.render(line, True, TEXT_COLOR)
            self.display_surface.blit(text_surf, (description_rect.x + 10, description_rect.y + 10 + i * 25))    # 정보 - 스킬 창

    def show_skills_tab(self, rect, battler):
        """스킬 탭 내용 표시"""
        padding_x = 15
        padding_y = 15
        column_width = (rect.width // 2) - (padding_x * 2)
        description_x = rect.x + (rect.width // 2) + padding_x
        description_width = (rect.width // 2) - (padding_x * 2)
        
        # 스킬 영역 계산
        skill_height = 30
        skill_spacing = 10
        skills_start_y = rect.y + padding_y
        
        # 전체 스킬 리스트와 표시 가능한 스킬 수 계산
        all_skills = list(battler.skills.items())
        visible_skills = 8  # 한 번에 보여줄 스킬 수
        max_skills = len(all_skills)
        
        # 스크롤 위치 계산 (info_skill_index를 기준으로)
        scroll_offset = max(0, min(self.info_skill_index - (visible_skills - 2), max_skills - visible_skills))
        visible_skills_list = all_skills[scroll_offset:scroll_offset + visible_skills]
        
        # 화살표 애니메이션을 위한 타이밍 계산
        current_time = pygame.time.get_ticks()
        arrow_offset = abs(math.sin(current_time / 300)) * 5  # 부드러운 상하 움직임
        
        # 스크롤 화살표 표시
        arrow_size = 20
        arrow_color = UI_BORDER_COLOR
        if scroll_offset > 0:  # 위쪽 화살표
            arrow_y = rect.y + padding_y
            points_up = [
                (rect.centerx - arrow_size//2, arrow_y + arrow_size - arrow_offset),
                (rect.centerx + arrow_size//2, arrow_y + arrow_size - arrow_offset),
                (rect.centerx, arrow_y - arrow_offset)
            ]
            pygame.draw.polygon(self.display_surface, arrow_color, points_up)
        
        if scroll_offset + visible_skills < max_skills:  # 아래쪽 화살표
            arrow_y = rect.bottom - padding_y - arrow_size
            points_down = [
                (rect.centerx - arrow_size//2, arrow_y + arrow_offset),
                (rect.centerx + arrow_size//2, arrow_y + arrow_offset),
                (rect.centerx, arrow_y + arrow_size + arrow_offset)
            ]
            pygame.draw.polygon(self.display_surface, arrow_color, points_down)

        # 스킬 리스트 표시
        for i, (skill_name, skill_level) in enumerate(visible_skills_list):
            skill_rect = pygame.Rect(
                rect.x + padding_x,
                skills_start_y + i * (skill_height + skill_spacing),
                column_width,
                skill_height
            )
            
            is_selected = (i + scroll_offset) == self.info_skill_index
            is_hovered = i + scroll_offset == getattr(self, 'hovered_skill', None)
            
            # 스킬 스타일
            skill_info = SKILL_PROPERTIES[skill_name]
            style_name = skill_info.get('Style', 'default')
            style = SKILL_STYLES[style_name]
            
            # 배경색 결정
            if is_selected:
                bg_color = UPGRADE_BG_COLOR_SELECTED
                text_color = TEXT_COLOR_SELECTED
            elif is_hovered:
                bg_color = (80, 80, 80)
                text_color = style['text_color']
            else:
                bg_color = UI_BG_COLOR
                text_color = style['text_color']
            
            pygame.draw.rect(self.display_surface, bg_color, skill_rect, border_radius=5)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, skill_rect, 1, border_radius=5)
            
            text = self.font.render(skill_name, True, text_color)
            self.display_surface.blit(text, (skill_rect.x + 10, skill_rect.y + (skill_height - text.get_height())//2))
            
            # 스킬 레벨 표시
            level_text = f"Lv.{skill_level}"
            level_surface = self.font.render(level_text, True, text_color)
            level_rect = level_surface.get_rect(
                midright=(skill_rect.right - 10, skill_rect.centery)
            )
            self.display_surface.blit(level_surface, level_rect)
        
        # 설명란
        description_rect = pygame.Rect(
            description_x,
            rect.y + padding_y,
            description_width,
            rect.height - padding_y * 2
        )
        pygame.draw.rect(self.display_surface, (UI_BG_COLOR[0]-20, UI_BG_COLOR[1]-20, UI_BG_COLOR[2]-20), 
                        description_rect, border_radius=5)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, description_rect, 1, border_radius=5)
        
        # 선택된 스킬 설명 표시
        if all_skills:
            selected_skill, skill_level = all_skills[self.info_skill_index]
            skill_info = SKILL_PROPERTIES[selected_skill]
            description = skill_info['Description'].strip()
            format_dict = {}
            
            # Handle both active and passive skills
            if skill_info.get('Type') == 'Passive' and 'Passive' in skill_info:
                if 'condition' in skill_info['Passive']:
                    threshold = skill_info['Passive']['condition'].get('threshold', {}).get(skill_level)
                    if threshold is not None:
                        format_dict['threshold'] = threshold
            
            # Handle regular skill properties
            for key, value in skill_info.items():
                if isinstance(value, dict) and skill_level in value:
                    if isinstance(value[skill_level], dict):
                        format_dict.update(value[skill_level])
                    else:
                        format_dict[key] = value[skill_level]
            try:
                description = description.format(**format_dict)
            except KeyError:
                pass
            
            # 설명 텍스트 표시
            description_lines = self.wrap_text(description, self.font, description_width - 20)
            for i, line in enumerate(description_lines[:10]):  # 최대 10줄까지 표시
                text_surf = self.font.render(line, True, TEXT_COLOR)
                self.display_surface.blit(text_surf, (description_rect.x + 10, description_rect.y + 10 + i * 25))

    def show_profile_tab(self, rect, battler):
        """프로필 탭 내용 표시 (추후 구현)"""
        text = self.font.render("프로필 정보 (미구현)", True, TEXT_COLOR)
        self.display_surface.blit(text, (rect.x + 10, rect.y + 10))

    def reset_info_menu_indexes(self):
        """정보 메뉴 인덱스 초기화"""
        self.info_tab = 'items'
        self.info_item_index = 0
        self.info_equip_index = 0
        self.info_skill_index = 0
        self.in_equip_section = False

    def wrap_text(self, text, font, max_width):
        """텍스트를 주어진 너비에 맞게 여러 줄로 나눔"""
        words = text.split(' ')
        lines = []
        current_line = []
        current_width = 0

        for word in words:
            word_surface = font.render(word + ' ', True, TEXT_COLOR)
            word_width = word_surface.get_width()

            if current_width + word_width <= max_width:
                current_line.append(word)
                current_width += word_width
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width

        if current_line:
            lines.append(' '.join(current_line))
        return lines

    def player_menu_control(self):
        """플레이어 메뉴 조작 및 커맨드 생성"""
        selected_battler = self.level.map_action.selected_battler
        if self.previous_main_menu != self.neutral_main_menu:
            self.previous_main_menu = self.neutral_main_menu
        elif self.neutral_main_menu != self.current_main_menu:
            self.neutral_main_menu = self.current_main_menu
            

        if not selected_battler:
            print('return')
            return None
        if self.current_main_menu == 'range':
            return ['사격타겟지정']
        elif self.current_main_menu[:5] == 'skill':
            return self.handle_skill_menu()
        elif self.current_main_menu == 'item':
            return self.handle_item_menu()
        elif self.current_main_menu == 'info':
            if self.previous_main_menu != self.current_main_menu:
                self.reset_info_menu_indexes()
            return self.handle_info_menu()
        
        elif self.current_main_menu == 'wait':
            return ['대기']
            
        elif self.current_main_menu == 'main':
            return self.handle_main_menu()  

    def handle_main_menu(self):
        selected_battler = self.level.map_action.selected_battler
        char_data = CharacterDatabase.data.get(selected_battler.char_type, {})
        menu_actions = []
        menu_rects = {}  # 각 메뉴 항목의 rect를 저장
        
        # 메뉴 항목 구성
        if char_data.get('Class') == 'Range' and not selected_battler.inactive:
            menu_actions.append('range')
        
        active_skills = [skill for skill in selected_battler.skills if SKILL_PROPERTIES[skill]['Type'] == 'Active']
        if active_skills and not selected_battler.inactive:
            menu_actions.append('skill')
        
        if selected_battler.inventory and not selected_battler.inactive:
            menu_actions.append('item')
        
        menu_actions.extend(['info'])

        if not selected_battler.inactive:
            menu_actions.extend(['wait'])

        # 메뉴 위치 계산
        screen_width = self.display_surface.get_width()
        battler_screen_x = selected_battler.rect.centerx - self.visible_sprites.offset.x
        is_on_left = battler_screen_x < screen_width / 2

        if is_on_left:
            base_x = selected_battler.rect.right - self.visible_sprites.offset.x + MENU_OFFSET
        else:
            base_x = selected_battler.rect.left - self.visible_sprites.offset.x - MENU_PANEL_WIDTH - MENU_OFFSET
        base_y = selected_battler.rect.centery - self.visible_sprites.offset.y - (len(menu_actions) * MENU_PANEL_HEIGHT + MENU_PANEL_SPACING)

        # 각 메뉴 항목의 rect 생성 및 마우스 체크
        mouse_pos = self.input_manager.get_mouse_pos()
        for i, action in enumerate(menu_actions):
            menu_rect = pygame.Rect(base_x,base_y + i * (MENU_PANEL_HEIGHT + MENU_PANEL_SPACING),MENU_PANEL_WIDTH,MENU_PANEL_HEIGHT)
            menu_rects[action] = menu_rect
            
            # 마우스가 메뉴 위에 있으면 호버
            if self.input_manager.is_mouse_in_rect(menu_rect):
                if self.input_manager.is_left_click():
                    self.current_main_menu = action
                    return [action] if action in ['range', 'wait'] else None
                
                

        # 키보드 입력 처리 (기존 코드 유지)
        if self.selected_menu == 'init':
            self.selected_menu = menu_actions[0]
            self.current_skill_menu_index = 0
            self.current_item_menu_index = 0
        if self.input_manager.is_just_pressed('Select'):
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_SELECT'])
            self.current_main_menu = self.selected_menu
            return [self.selected_menu] if self.selected_menu in ['range', 'wait'] else None
        elif self.input_manager.is_just_pressed('Down'):
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])
            self.selected_menu = menu_actions[(menu_actions.index(self.selected_menu) + 1) % len(menu_actions)]
        elif self.input_manager.is_just_pressed('Up'):
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])
            self.selected_menu = menu_actions[(menu_actions.index(self.selected_menu) - 1) % len(menu_actions)]
        elif self.input_manager.is_just_pressed('Cancel') or self.input_manager.is_right_click():
            return ['취소']

        return None

    def handle_skill_menu(self):
        """스킬 메뉴 처리"""
        selected_battler = self.level.map_action.selected_battler
        active_skills = [skill for skill in selected_battler.skills 
                        if SKILL_PROPERTIES[skill]['Type'] == 'Active']

        skill_menu_width = MENU_PANEL_WIDTH * 2.5
        description_height = MENU_PANEL_HEIGHT * 1.5  # 설명란 높이
        skills_start_y = MENU_PANEL_HEIGHT * 2  # 스킬 목록 시작 위치
        skill_menu_height = skills_start_y + (MENU_PANEL_HEIGHT + 10) * len(active_skills)

        # 메뉴 위치 계산
        screen_width = self.display_surface.get_width()
        battler_screen_x = selected_battler.rect.centerx - self.visible_sprites.offset.x
        is_on_left = battler_screen_x < screen_width / 2

        if is_on_left:
            base_x = selected_battler.rect.right - self.visible_sprites.offset.x + MENU_OFFSET
        else:
            base_x = selected_battler.rect.left - self.visible_sprites.offset.x - skill_menu_width - MENU_OFFSET

        base_y = selected_battler.rect.centery - self.visible_sprites.offset.y - skill_menu_height // 2

        # 각 스킬 항목의 rect 체크
        for i, skill in enumerate(active_skills):
            skill_rect = pygame.Rect(
                base_x + 10,
                base_y + skills_start_y + i * (MENU_PANEL_HEIGHT + 10),
                skill_menu_width - 20,
                MENU_PANEL_HEIGHT
            )
            
            if self.input_manager.is_mouse_in_rect(skill_rect):
                if self.input_manager.is_left_click():
                    if self.current_skill_menu_index == i:
                        skill_level = selected_battler.skills[skill]
                        if 'Mana' in SKILL_PROPERTIES[skill]:
                            mana_cost = SKILL_PROPERTIES[skill]['Mana'][skill_level]
                            if selected_battler.Cur_MP < mana_cost:
                                return None
                        self.current_main_menu = self.previous_main_menu = self.neutral_main_menu = 'skill_target'
                        return ['스킬타겟지정', skill]
                    self.current_skill_menu_index = i

        # 마우스 휠 처리
        wheel_movement = self.input_manager.get_wheel_movement()

        # 키보드 입력 처리 (기존 코드)
        if self.input_manager.is_just_pressed('Up') or wheel_movement > 0:
            self.current_skill_menu_index = (self.current_skill_menu_index - 1) % len(active_skills)
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])
        elif self.input_manager.is_just_pressed('Down') or wheel_movement < 0:
            self.current_skill_menu_index = (self.current_skill_menu_index + 1) % len(active_skills)
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])
        elif self.input_manager.is_just_pressed('Select'):
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_SELECT'])
            selected_skill = active_skills[self.current_skill_menu_index]
            skill_level = selected_battler.skills[selected_skill]
            if 'Mana' in SKILL_PROPERTIES[selected_skill]:
                mana_cost = SKILL_PROPERTIES[selected_skill]['Mana'][skill_level]
                if selected_battler.Cur_MP < mana_cost:
                    return None
            self.current_main_menu = self.previous_main_menu = self.neutral_main_menu = 'skill_target'
            return ['스킬타겟지정', selected_skill]
        elif (self.input_manager.is_just_pressed('Cancel') or 
            self.input_manager.is_right_click()) and self.previous_main_menu == 'skill':
            self.current_main_menu = 'main'
            self.selected_menu = 'skill'

        return None

    def handle_item_menu(self):
        """아이템 메뉴 처리"""
        selected_battler = self.level.map_action.selected_battler
        
        # show_item_menu와 동일한 계산
        item_menu_width = MENU_PANEL_WIDTH * 2.5
        items_start_y = MENU_PANEL_HEIGHT * 2
        items_display_count = min(4, len(selected_battler.inventory))
        item_menu_height = items_start_y + (MENU_PANEL_HEIGHT + 10) * items_display_count

        screen_width = self.display_surface.get_width()
        battler_screen_x = selected_battler.rect.centerx - self.visible_sprites.offset.x
        is_on_left = battler_screen_x < screen_width / 2

        if is_on_left:
            base_x = selected_battler.rect.right - self.visible_sprites.offset.x + MENU_OFFSET
        else:
            base_x = selected_battler.rect.left - self.visible_sprites.offset.x - item_menu_width - MENU_OFFSET

        base_y = selected_battler.rect.centery - self.visible_sprites.offset.y - item_menu_height // 2

        # 각 아이템 항목에 대한 rect 확인 및 마우스 입력 처리
        for i, item in enumerate(selected_battler.inventory[:items_display_count]):
            item_rect = pygame.Rect(
                base_x + 10,
                base_y + items_start_y + i * (MENU_PANEL_HEIGHT + 10),
                item_menu_width - 20,
                MENU_PANEL_HEIGHT
            )
            
            # 마우스가 아이템 위에 있을 때
            if self.input_manager.is_mouse_in_rect(item_rect):
                # 클릭 처리
                if self.input_manager.is_left_click():
                    if self.current_item_menu_index == i:
                        return ['아이템사용', item]
                    self.current_item_menu_index = i

        # 마우스 휠 처리
        wheel_movement = self.input_manager.get_wheel_movement()
        if wheel_movement > 0:
            self.current_item_menu_index = (self.current_item_menu_index - 1) % len(selected_battler.inventory)
        elif wheel_movement < 0:
            self.current_item_menu_index = (self.current_item_menu_index + 1) % len(selected_battler.inventory)

        # 키보드 입력 처리
        if self.input_manager.is_just_pressed('Up'):
            self.current_item_menu_index = (self.current_item_menu_index - 1) % len(selected_battler.inventory)
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])
        elif self.input_manager.is_just_pressed('Down'):
            self.current_item_menu_index = (self.current_item_menu_index + 1) % len(selected_battler.inventory)
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])
        elif self.input_manager.is_just_pressed('Select'):
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_SELECT'])
            selected_item = selected_battler.inventory[self.current_item_menu_index]
            return ['아이템사용', selected_item]
        elif (self.input_manager.is_just_pressed('Cancel') or 
              self.input_manager.is_right_click()) and self.previous_main_menu == 'item':
            self.current_main_menu = 'main'
            self.selected_menu = 'item'

        return None

    def handle_info_menu(self):
        """정보 메뉴 조작"""
        selected_battler = self.level.map_action.selected_battler
        if not selected_battler:
            return

        # 마우스 호버 상태 초기화
        self.hovered_item = None
        self.hovered_equip = None
        self.hovered_skill = None
        self.hovered_tab = None

        # 탭 영역 계산
        menu_width = MENU_PANEL_WIDTH * 3
        menu_height = MENU_PANEL_HEIGHT * 10
        tab_width = menu_width // 3
        tab_height = 30
        
        # 메뉴 위치 계산
        screen_width = self.display_surface.get_width()
        battler_screen_x = selected_battler.rect.centerx - self.visible_sprites.offset.x
        is_on_left = battler_screen_x < screen_width / 2
        
        if is_on_left:
            base_x = selected_battler.rect.right - self.visible_sprites.offset.x + MENU_OFFSET
        else:
            base_x = selected_battler.rect.left - self.visible_sprites.offset.x - menu_width - MENU_OFFSET
        base_y = selected_battler.rect.centery - self.visible_sprites.offset.y - menu_height // 2

        # 마우스 위치
        mouse_pos = self.input_manager.get_mouse_pos()

        # 탭 클릭 및 호버 처리
        tabs = [('인벤토리', 'items'), ('스킬', 'skills'), ('정보', 'profile')]
        for i, (tab_name, tab_id) in enumerate(tabs):
            tab_rect = pygame.Rect(base_x + i * tab_width, base_y, tab_width, tab_height)
            if self.input_manager.is_mouse_in_rect(tab_rect):
                self.hovered_tab = tab_id
                if self.input_manager.is_left_click():
                    self.info_tab = tab_id
                    self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])

        # 컨텐츠 영역 계산
        content_rect = pygame.Rect(base_x, base_y + tab_height, menu_width, menu_height - tab_height)

        # 현재 탭에 따른 마우스 처리
        if self.info_tab == 'items':
            # 아이템 섹션 영역 계산
            padding_x = 15
            padding_y = 15
            item_box_height = 28
            item_box_spacing = 4
            items_start_y = base_y + tab_height + 45

            # 아이템 영역 클릭 및 호버 처리
            for i, item in enumerate(selected_battler.inventory):
                item_rect = pygame.Rect(
                    base_x + padding_x,
                    items_start_y + i * (item_box_height + item_box_spacing),
                    menu_width // 2 - padding_x * 2,
                    item_box_height
                )
                if self.input_manager.is_mouse_in_rect(item_rect):
                    self.hovered_item = i
                    if self.input_manager.is_left_click():
                        self.in_equip_section = False
                        self.info_item_index = i
                        self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])

            # 장비 섹션 영역 계산
            equip_title_y = items_start_y + len(selected_battler.inventory) * (item_box_height + item_box_spacing) + 25
            equip_start_y = equip_title_y + 30

            # 장비 영역 클릭 및 호버 처리
            for i, equip in enumerate(selected_battler.equips):
                equip_rect = pygame.Rect(
                    base_x + padding_x,
                    equip_start_y + i * (item_box_height + item_box_spacing),
                    menu_width // 2 - padding_x * 2,
                    item_box_height
                )
                if self.input_manager.is_mouse_in_rect(equip_rect):
                    self.hovered_equip = i
                    if self.input_manager.is_left_click():
                        self.in_equip_section = True
                        self.info_equip_index = i
                        self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])

        elif self.info_tab == 'skills':
            # 스킬 영역 계산
            padding_y = 10
            skill_height = 30
            skill_spacing = 10
            skills_start_y = base_y + tab_height + padding_y

            # 스킬 리스트 클릭 및 호버 처리
            all_skills = list(selected_battler.skills.items())
            visible_skills = 8
            for i, (skill_name, _) in enumerate(all_skills[:visible_skills]):
                skill_rect = pygame.Rect(
                    base_x + 10,
                    skills_start_y + i * 40,
                    menu_width // 2 - 20,
                    skill_height
                )
                if self.input_manager.is_mouse_in_rect(skill_rect):
                    self.hovered_skill = i
                    if self.input_manager.is_left_click():
                        self.info_skill_index = i
                        self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])

        # 마우스 휠 처리
        wheel_movement = self.input_manager.get_wheel_movement()


        # 키보드 입력 처리
        if self.input_manager.is_just_pressed('Right'):
            tabs = ['items', 'skills', 'profile']
            current_index = tabs.index(self.info_tab)
            self.info_tab = tabs[(current_index + 1) % len(tabs)]
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])
        elif self.input_manager.is_just_pressed('Left'):
            tabs = ['items', 'skills', 'profile']
            current_index = tabs.index(self.info_tab)
            self.info_tab = tabs[(current_index - 1) % len(tabs)]
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])
        elif self.input_manager.is_just_pressed('Up') or wheel_movement > 0:
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])
            if self.info_tab == 'items':
                if self.in_equip_section:
                    # 장비 섹션에서 위로 이동
                    if self.info_equip_index > 0:
                        self.info_equip_index -= 1
                    else:
                        # 장비 섹션 맨 위에서 위로 가면 아이템 섹션 맨 아래로
                        self.in_equip_section = False
                        if selected_battler.inventory:
                            self.info_item_index = len(selected_battler.inventory) - 1
                else:
                    # 아이템 섹션에서 위로 이동
                    if self.info_item_index > 0:
                        self.info_item_index -= 1
                    else:
                        # 아이템 섹션 맨 위에서 위로 가면 장비 섹션 맨 아래로
                        if selected_battler.equips:
                            self.in_equip_section = True
                            self.info_equip_index = len(selected_battler.equips) - 1
            elif self.info_tab == 'skills':
                max_skills = len(selected_battler.skills)
                if max_skills > 0:
                    self.info_skill_index = (self.info_skill_index - 1) % max_skills

        elif self.input_manager.is_just_pressed('Down') or wheel_movement < 0:
            self.sound_manager.play_sound(**SOUND_PROPERTIES['MENU_MOVE'])
            if self.info_tab == 'items':
                if self.in_equip_section:
                    # 장비 섹션에서 아래로 이동
                    if self.info_equip_index < len(selected_battler.equips) - 1:
                        self.info_equip_index += 1
                    else:
                        # 장비 섹션 맨 아래에서 아래로 가면 아이템 섹션 맨 위로
                        self.in_equip_section = False
                        self.info_item_index = 0 if selected_battler.inventory else 0
                else:
                    # 아이템 섹션에서 아래로 이동
                    if self.info_item_index < len(selected_battler.inventory) - 1:
                        self.info_item_index += 1
                    else:
                        # 아이템 섹션 맨 아래에서 아래로 가면 장비 섹션 맨 위로
                        if selected_battler.equips:
                            self.in_equip_section = True
                            self.info_equip_index = 0
            elif self.info_tab == 'skills':
                max_skills = len(selected_battler.skills)
                if max_skills > 0:
                    self.info_skill_index = (self.info_skill_index + 1) % max_skills
        elif (self.input_manager.is_just_pressed('Cancel') or 
            self.input_manager.is_right_click()) and self.previous_main_menu == 'info':
            self.current_main_menu = 'main'
            self.selected_menu = 'info'
            return


        return None

    def show_items_tab(self, rect, battler):
        """인벤토리 탭 내용 표시"""
        section_font = pygame.font.Font(UI_FONT, 18)
        normal_font = self.font
        
        padding_x = 15
        padding_y = 15
        column_width = (rect.width // 2) - (padding_x * 2)
        description_x = rect.x + (rect.width // 2) + padding_x
        description_width = (rect.width // 2) - (padding_x * 2)
        
        item_box_height = 28
        item_box_spacing = 4
        icon_size = 24  # 아이콘 크기
        icon_padding = 2  # 아이콘 주변 여백
        name_padding = 10  # 아이콘과 이름 사이의 간격
        
        # 아이템/장비 보유 상태에 따라 인덱스 조정
        if not battler.inventory and battler.equips:
            self.in_equip_section = True
            self.info_item_index = 0
            self.info_equip_index = 0
        elif not battler.inventory and not battler.equips:
            self.in_equip_section = False
            self.info_item_index = 0
            self.info_equip_index = 0

        # 아이템 섹션
        items_title_y = rect.y + padding_y
        items_text = section_font.render("아이템", True, TEXT_COLOR)
        self.display_surface.blit(items_text, (rect.x + padding_x, items_title_y))
        
        items_start_y = items_title_y + 30
        num_items = min(4, len(battler.inventory))
        
        for i in range(num_items):
            item = battler.inventory[i]
            item_rect = pygame.Rect(
                rect.x + padding_x,
                items_start_y + i * (item_box_height + item_box_spacing),
                column_width,
                item_box_height
            )
            
            is_selected = (i == self.info_item_index and not self.in_equip_section)
            is_hovered = i == getattr(self, 'hovered_item', None)
            
            # 배경색 결정 (선택됨 > 호버 > 기본)
            if is_selected:
                bg_color = UPGRADE_BG_COLOR_SELECTED
                text_color = TEXT_COLOR_SELECTED
            elif is_hovered:
                bg_color = (80, 80, 80)
                text_color = TEXT_COLOR
            else:
                bg_color = UI_BG_COLOR
                text_color = TEXT_COLOR
            
            pygame.draw.rect(self.display_surface, bg_color, item_rect, border_radius=5)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, item_rect, 1, border_radius=5)
            
            # 아이콘 로드 및 표시
            item_info = ITEM_PROPERTIES[item]
            if 'icon_path' in item_info:
                try:
                    icon = pygame.image.load(item_info['icon_path']).convert_alpha()
                    icon = pygame.transform.scale(icon, (icon_size, icon_size))
                    icon_x = item_rect.x + icon_padding
                    icon_y = item_rect.centery - icon_size // 2
                    self.display_surface.blit(icon, (icon_x, icon_y))
                except:
                    print(f"아이콘 로드 실패: {item_info['icon_path']}")
                    # 아이콘 로드 실패 시 기본 아이콘이나 빈 공간으로 처리
                    pass
            
            # 아이템 이름은 아이콘 오른쪽에 표시
            text = normal_font.render(item_info['name'], True, text_color)
            text_x = item_rect.x + icon_size + name_padding
            text_y = item_rect.centery - text.get_height() // 2
            self.display_surface.blit(text, (text_x, text_y))
        
        items_section_height = num_items * (item_box_height + item_box_spacing)

        # 장비 섹션
        equip_title_y = items_start_y + items_section_height + 25
        equip_text = section_font.render("장비", True, TEXT_COLOR)
        self.display_surface.blit(equip_text, (rect.x + padding_x, equip_title_y))
        
        equip_start_y = equip_title_y + 30
        num_equips = min(4, len(battler.equips))
        
        for i in range(num_equips):
            equip = battler.equips[i]
            equip_rect = pygame.Rect(
                rect.x + padding_x,
                equip_start_y + i * (item_box_height + item_box_spacing),
                column_width,
                item_box_height
            )
            
            is_selected = (i == self.info_equip_index and self.in_equip_section)
            is_hovered = i == getattr(self, 'hovered_equip', None)
            
            # 배경색 결정
            if is_selected:
                bg_color = UPGRADE_BG_COLOR_SELECTED
                text_color = TEXT_COLOR_SELECTED
            elif is_hovered:
                bg_color = (80, 80, 80)
                text_color = TEXT_COLOR
            else:
                bg_color = UI_BG_COLOR
                text_color = TEXT_COLOR
            
            pygame.draw.rect(self.display_surface, bg_color, equip_rect, border_radius=5)
            pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, equip_rect, 1, border_radius=5)
            
            # 장비 아이콘 로드 및 표시
            equip_info = EQUIP_PROPERTIES[equip]
            if 'icon_path' in equip_info:
                try:
                    icon = pygame.image.load(equip_info['icon_path']).convert_alpha()
                    icon = pygame.transform.scale(icon, (icon_size, icon_size))
                    icon_x = equip_rect.x + icon_padding
                    icon_y = equip_rect.centery - icon_size // 2
                    self.display_surface.blit(icon, (icon_x, icon_y))
                except:
                    print(f"아이콘 로드 실패: {equip_info['icon_path']}")
                    # 아이콘 로드 실패 시 기본 아이콘이나 빈 공간으로 처리
                    pass
            
            # 장비 이름은 아이콘 오른쪽에 표시
            text = normal_font.render(equip, True, text_color)
            text_x = equip_rect.x + icon_size + name_padding
            text_y = equip_rect.centery - text.get_height() // 2
            self.display_surface.blit(text, (text_x, text_y))
        
        # 설명란
        description_rect = pygame.Rect(
            description_x,
            rect.y + padding_y,
            description_width,
            rect.height - padding_y * 2
        )
        pygame.draw.rect(
            self.display_surface, 
            (UI_BG_COLOR[0]-20, UI_BG_COLOR[1]-20, UI_BG_COLOR[2]-20), 
            description_rect, 
            border_radius=5
        )
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, description_rect, 1, border_radius=5)
        
        # 선택된 아이템/장비의 설명 표시
        description = ""
        if self.in_equip_section and battler.equips and 0 <= self.info_equip_index < len(battler.equips):
            selected_item = battler.equips[self.info_equip_index]
            description = EQUIP_PROPERTIES[selected_item]['Description']
        elif not self.in_equip_section and battler.inventory and 0 <= self.info_item_index < len(battler.inventory):
            selected_item = battler.inventory[self.info_item_index]
            description = ITEM_PROPERTIES[selected_item]['Description']
        
        description_lines = self.wrap_text(description, normal_font, description_rect.width - 20)
        for i, line in enumerate(description_lines[:10]):
            text_surf = normal_font.render(line, True, TEXT_COLOR)
            self.display_surface.blit(text_surf, (description_rect.x + 10, description_rect.y + 10 + i * 25))

    def display(self):

        # 대화상자가 있는지 확인
        if self.level.map_action.current_dialog is not None:
            # print(self.level.map_action.current_dialog)
            return

        if self.level.map_action.current_state == "player_menu":
            if self.current_main_menu == 'skill':
                self.show_skill_menu(self.current_skill_menu_index)
            elif self.current_main_menu == 'item':
                self.show_item_menu(self.current_item_menu_index)
            elif self.current_main_menu == 'info':  # 여기에 info 메뉴 추가
                self.show_info_menu()
            elif self.current_main_menu == 'main':
                self.show_player_menu(self.selected_menu)
        elif self.level.map_action.current_state == "player_control":
            self.show_Moves()
        # 대화상자가 없을 때만 캐릭터 UI 표시
        elif (str(self.level.map_action.current_state) == 'explore' or str(self.level.map_action.current_state) == 'select_target'):
            cursor_pos = self.level.cursor.pos
            character_on_cursor = None
            for battler in self.level.battler_sprites:
                if battler.pos == cursor_pos:
                    character_on_cursor = battler
                    break
            if character_on_cursor:
                self.show_characterUI(character_on_cursor)
            elif self.level.map_action.current_state == "explore":
                self.show_cursorUI()
                
class ConfirmationDialog:
    def __init__(self, message="이동합니까?"):  # 메시지를 파라미터로 받도록 수정
        self.message = message  # 메시지 저장
        self.display_surface = pygame.display.get_surface()
        self.font = pygame.font.Font(UI_FONT, 16)
        self.width = 200
        self.height = 100
        self.x = (WIDTH - self.width) // 2
        self.y = (HEIGHT - self.height) // 2
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.yes_rect = pygame.Rect(self.x + 30, self.y + 60, 60, 30)
        self.no_rect = pygame.Rect(self.x + 110, self.y + 60, 60, 30)
        
        # 선택 상태 관리
        self.selected_option = 'yes'  # 'yes' 또는 'no'
        self.mouse_hover = None  # 마우스가 올라간 버튼

    def draw(self):
        # 반투명 오버레이
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.display_surface.blit(overlay, (0, 0))
        
        # 메인 창
        pygame.draw.rect(self.display_surface, UI_BG_COLOR, self.rect, border_radius=10)
        pygame.draw.rect(self.display_surface, UI_BORDER_COLOR, self.rect, 2, border_radius=10)
        
        # 제목 텍스트
        text = self.font.render(self.message, True, TEXT_COLOR)
        text_rect = text.get_rect(center=(self.x + self.width//2, self.y + 30))
        self.display_surface.blit(text, text_rect)
        
        # 버튼
        buttons = [
            (self.yes_rect, "예", 'yes'),
            (self.no_rect, "아니오", 'no')
        ]
        
        for rect, text, option in buttons:
            # 버튼 배경 색상 결정
            if option == self.selected_option or option == self.mouse_hover:
                bg_color = UPGRADE_BG_COLOR_SELECTED
                text_color = TEXT_COLOR_SELECTED
                border_color = UI_BORDER_COLOR_ACTIVE
            else:
                bg_color = UI_BG_COLOR
                text_color = TEXT_COLOR
                border_color = UI_BORDER_COLOR
            
            # 버튼 그리기
            pygame.draw.rect(self.display_surface, bg_color, rect, border_radius=5)
            pygame.draw.rect(self.display_surface, border_color, rect, 2, border_radius=5)
            
            # 텍스트 그리기
            text_surf = self.font.render(text, True, text_color)
            text_rect = text_surf.get_rect(center=rect.center)
            self.display_surface.blit(text_surf, text_rect)

    def handle_input(self, input_manager):
        
        mouse_pos = pygame.mouse.get_pos()
        
        # 마우스 호버 상태 업데이트
        self.mouse_hover = None
        if self.yes_rect.collidepoint(mouse_pos):
            self.mouse_hover = 'yes'
        elif self.no_rect.collidepoint(mouse_pos):
            self.mouse_hover = 'no'
        
        # 키보드 입력 처리
        if input_manager.is_just_pressed('Left'):
            self.selected_option = 'yes'
        elif input_manager.is_just_pressed('Right'):
            self.selected_option = 'no'
        
        # 선택 처리
        if input_manager.is_just_pressed('Select'):
            input_manager.reset_mouse_state()  # 선택 후 마우스 상태 초기화
            return self.selected_option == 'yes'
        
        # 마우스 클릭 처리
        if input_manager.is_left_click():
            if self.yes_rect.collidepoint(mouse_pos):
                input_manager.reset_mouse_state()  # 선택 후 마우스 상태 초기화
                return True
            if self.no_rect.collidepoint(mouse_pos):
                input_manager.reset_mouse_state()  # 선택 후 마우스 상태 초기화
                return False
        
        # 취소 처리
        if input_manager.is_just_pressed('Cancel') or input_manager.is_right_click():
            input_manager.reset_mouse_state()  # 취소 후 마우스 상태 초기화
            return False
            
        return None
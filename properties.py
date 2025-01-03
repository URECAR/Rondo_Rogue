# properties.py
import pygame
# game setup
WIDTH    = 1280	
HEIGHT   = 720
FPS      = 60
TILESIZE = 64
CAMERA_MARGIN_X = 7.5 * TILESIZE
CAMERA_MARGIN_Y = 3 * TILESIZE

KEY_SETS = {
    'Select' : [pygame.K_SPACE, pygame.K_c],
    'Cancel' : [pygame.K_ESCAPE, pygame.K_x],
    'Check' : [pygame.K_f],
    'Menu' : [pygame.K_m],
    'Up' : [pygame.K_UP],
    'Down' : [pygame.K_DOWN],
    'Left' : [pygame.K_LEFT],
    'Right' : [pygame.K_RIGHT],
    'Previous' : [pygame.K_q],
    'Next' : [pygame.K_e],
    
}

# ui
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ENERGY_BAR_WIDTH = 140
ITEM_BOX_SIZE = 80
UI_FONT = '../graphics/font/Galmuri7.ttf'
UI_FONT_SIZE = 64
GENERAL_FONT = '../graphics/font/KCC-Ganpan.ttf'
# UI panel settings
MENU_PANEL_WIDTH = 150
MENU_PANEL_HEIGHT = 40
MENU_PANEL_SPACING = 2
PANEL_BORDER_RADIUS = 15
CHARACTER_PANEL_WIDTH = 180
CHARACTER_PANEL_HEIGHT = 160
CHARACTER_LINE_SPACING = 24
MENU_OFFSET = 10  # 메뉴와 캐릭터 사이 간격
PANEL_ALPHA = 220  # 패널 투명도


# general colors
CURSOR_BASIC_COLOR = '#A6A6A6'
CURSOR_BORDER_COLOR = '#D4F4FA'
CURSOR_SELECTED_COLOR = 'Yellow'
WATER_COLOR = '#71DDEE'
UI_BG_COLOR = (64, 64, 64)  # RGB 튜플로 정의
UI_BORDER_COLOR = (200, 200, 200)
UI_BORDER_COLOR_ACTIVE = (255, 255, 255)
UPGRADE_BG_COLOR_SELECTED = (100, 100, 100)
TEXT_COLOR = '#EEEEEE'
HIDDEN_STAT_COLOR = '#FF0000'
# ui colors
HEALTH_COLOR = 'red'
ENERGY_COLOR = '#5AFFFF'
EXP_COLOR   =  '#ABF200'

# upgrade menu
TEXT_COLOR_SELECTED = '#111111'
BAR_COLOR = '#EEEEEE'
BAR_COLOR_SELECTED = '#111111'
DIRECTIONS = ['UP', 'LEFT', 'DOWN', 'RIGHT']

# sound settings
INITIAL_MASTER_VOLUME = 0.0
INITIAL_MUSIC_VOLUME = 0.5
INITIAL_SFX_VOLUME = 0.5


SKILL_STYLES = {
   'default': {  # 기본 스타일
       'border_color': (192, 192, 192),  # 실버
       'text_color': (255, 255, 255),    # 흰색
       'bg_color': (0, 0, 0, 200)        # 반투명 검정
   },
   'magic': {    # 마법 스킬용
       'border_color': (100, 149, 237),  # 파란색 
       'text_color': (135, 206, 235),    # 하늘색
       'bg_color': (0, 0, 0, 200)        
   },
   'support': {   # 버프/지원 스킬용
       'border_color': (218, 165, 32),   # 골드
       'text_color': (255, 215, 0),      # 노란색
       'bg_color': (0, 0, 0, 200)
   },
   'red': {      # 공격 스킬용 
       'border_color': (178, 34, 34),    # 빨간색
       'text_color': (255, 99, 71),      # 밝은 빨간색
       'bg_color': (0, 0, 0, 200)
   },
   'purple': {   # 디버프 스킬용
       'border_color': (147, 112, 219),  # 보라색
       'text_color': (218, 112, 214),    # 밝은 보라
       'bg_color': (0, 0, 0, 200)
   }
}

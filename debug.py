import pygame
from properties import *

pygame.init()
font = pygame.font.Font(GENERAL_FONT,10)
line_length = 280
def debug(info, y=10, x=10):
    display_surface = pygame.display.get_surface()

    # info를 문자열로 변환
    text = str(info)
    
    # 긴 문자열을 여러 줄로 나누기
    lines = []
    start = 0
    while start < len(text):
        end = start + line_length
        lines.append(text[start:end])
        start = end
    
    # 각 줄을 출력
    current_y = y
    for line in lines:
        debug_surf = font.render(line, True, 'White')
        debug_rect = debug_surf.get_rect(topleft=(x, current_y))
        pygame.draw.rect(display_surface, 'Black', debug_rect)
        display_surface.blit(debug_surf, debug_rect)
        current_y += debug_rect.height
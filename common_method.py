# common_method.py
from database import SKILL_PROPERTIES
from csv import reader
from os import walk 
import pygame

def is_adjacent(battler1, battler2):
# 두 배틀러가 서로 붙었는 지 확인
    dx = abs(battler1.pos.x - battler2.pos.x)
    dy = abs(battler1.pos.y - battler2.pos.y)

    # 인접한지 확인
    return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

def print_if(SW, *args):
    if SW:
        print(*args)
        
def istarget(skill,selected_battler, battler,facing=None):
    skill_targets = SKILL_PROPERTIES[skill]['target']
    return (('Self_Ally' in skill_targets and (battler.team == selected_battler.team)) or
        ('Self_Ally_except_Self' in skill_targets and (battler.team == selected_battler.team) and battler != selected_battler) or
        ('Self_Enemy' in skill_targets and not (battler.team == selected_battler.team)))
    
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
            


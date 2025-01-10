# common_method.py
from database import SKILL_PROPERTIES
import csv
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
        layout = csv.reader(level_map,delimiter = ',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map
def combine_range_csvs(csv_paths):
    # 첫 번째 CSV를 읽어서 기본 크기 결정
    with open(csv_paths[0]) as f:
        reader = csv.reader(f)
        base_map = [row for row in reader]
    
    # 기본 맵의 크기
    height = len(base_map)
    width = len(base_map[0]) if height > 0 else 0
    
    # 결과 맵 초기화 (모두 -1로)
    result_map = [['-1' for _ in range(width)] for _ in range(height)]
    
    # 각 CSV 파일 처리
    for csv_path in csv_paths:
        with open(csv_path) as f:
            reader = csv.reader(f)
            current_map = [row for row in reader]
            
            # 각 위치 검사
            for y in range(height):
                for x in range(width):
                    current_value = current_map[y][x]
                    
                    # 현재 값이 -1이 아닌 경우
                    if current_value != '-1':
                        # 결과 맵의 현재 위치가 -1인 경우
                        if result_map[y][x] == '-1':
                            result_map[y][x] = [current_value]
                        # 결과 맵의 현재 위치가 이미 리스트인 경우
                        elif isinstance(result_map[y][x], list):
                            result_map[y][x].append(current_value)
                        # 결과 맵의 현재 위치가 단일 값인 경우
                        else:
                            result_map[y][x] = [current_value]
    
    return result_map

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
            


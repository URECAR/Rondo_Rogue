from database import SKILL_PROPERTIES
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
    
    
def Damage_Calculation(selected_battler, battler, type, is_critical = False,facing_judge = None):
    if type == 'Melee':
        pass
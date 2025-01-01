def is_adjacent(battler1, battler2):
# 두 배틀러가 서로 붙었는 지 확인
    dx = abs(battler1.pos.x - battler2.pos.x)
    dy = abs(battler1.pos.y - battler2.pos.y)

    # 인접한지 확인
    return (dx == 1 and dy == 0) or (dx == 0 and dy == 1)

def print_if(SW, *args):
    if SW:
        print(*args)
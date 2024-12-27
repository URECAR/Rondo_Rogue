# 2023-09-28 01:43 생성됨 #
import pygame, sys, os
from properties import *
from level import Level
from support import SoundManager,InputManager
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH,HEIGHT))
        pygame.display.set_caption('Not Rondo Of Swords')
        self.clock = pygame.time.Clock()
        self.sound_manager = SoundManager()  # 사운드 매니저 초기화
        self.input_manager = InputManager()
        self.level = Level()
    def run(self):
        while True:
            for event in pygame.event.get():
                # print(event)
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                self.input_manager.handle_input(event)
                self.sound_manager.handle_event(event)  # 사운드 이벤트 처리            self.screen.fill('black')
            self.level.run()
            self.input_manager.update()
            pygame.display.update()
            self.clock.tick(FPS)
if __name__ == '__main__':
    game = Game()
    game.run()

import pygame, sys
from overworld import Overworld
from settings import *
from level import Level
from ui import UI

class Game:
    def __init__(self) -> None:
        # właściwości gry
        self.max_level = 3
        self.max_health = 100
        self.current_health = 100
        self.coins = 0
        # muzyczka
        self.heal_sound = pygame.mixer.Sound('sounds/heal.mp3')
        self.level_bg_music = pygame.mixer.Sound('sounds/levels.wav')
        self.overworld_bg_music = pygame.mixer.Sound('sounds/overworld.wav')
        self.overworld_bg_music.play(loops = -1)
        # tworzenie menu głównego
        self.overworld = Overworld(0, self.max_level, screen, self.create_level)
        self.overworld_status = True
        # interfejs
        self.ui = UI(screen)

    def create_level(self, current_level):
        self.level = Level(current_level, screen, self.create_overworld, self.change_coins, self.change_health)
        self.overworld_status = False
        self.level_bg_music.play(loops= -1)
        self.overworld_bg_music.stop()

    def create_overworld(self, current_level, new_max_level):
        if new_max_level > self.max_level:
            self.max_level = new_max_level
        self.overworld = Overworld(current_level, self.max_level, screen, self.create_level)
        self.overworld_status = True
        self.overworld_bg_music.play(loops= -1)
        self.level_bg_music.stop()

    def change_coins(self, amount):
        self.coins += amount

    def change_health(self, amount):
        self.current_health += amount

    def check_game_over(self):
        if self.current_health <= 0:
            self.current_health = 100
            if self.coins >= 30:
                self.coins -= 30
                self.heal_sound.play()
            else:
                self.overworld = Overworld(0, self.max_level, screen, self.create_level)
                self.overworld_status = True
                self.overworld_bg_music.play(loops= -1)
                self.level_bg_music.stop()

    def run(self):
        if self.overworld_status:
            self.overworld.run()
        else:
            self.level.run()
            self.ui.show_health(self.current_health, self.max_health)
            self.ui.show_coins(self.coins)
            self.check_game_over()

pygame.init()
screen = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
game = Game()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    screen.fill('grey')
    game.run()

    pygame.display.update()
    clock.tick(60)
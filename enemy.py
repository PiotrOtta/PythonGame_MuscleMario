from random import randint
import pygame
from tiles import AnimatedTile

class Enemy(AnimatedTile):
    def __init__(self, size, x, y) -> None:
        super().__init__(size, x, y, 'graphics/enemy/run')
        self.rect = self.image.get_rect(center = (x, y))
        self.speed = randint(2, 5) * -1

    def move(self):
        self.rect.x += self.speed
    
    def reverse_image(self):
        if self.speed < 0:
            self.image = pygame.transform.flip(self.image, True, False)
    
    def reverse(self):
        self.speed *= -1

    def update(self, shift):
        self.rect.x += shift
        self.animate()
        self.move()
        self.reverse_image()
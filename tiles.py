import pygame

from extender import import_folder

class Tile(pygame.sprite.Sprite):
    def __init__(self, size, x, y) -> None:
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.rect = self.image.get_rect(topleft = (x, y))

    def update(self, x_shift) -> None:
        self.rect.x += x_shift

class StaticTile(Tile):
    def __init__(self, size, x, y, surface) -> None:
        super().__init__(size, x, y)
        self.image = surface

class AnimatedTile(Tile):
    def __init__(self, size, x, y, path) -> None:
        super().__init__(size, x, y)
        self.frames = import_folder(path)
        self.frame_index = 0
        self.image = self.frames[self.frame_index]

    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.frames[int(self.frame_index)]

    def update(self, x_shift) -> None:
        self.animate()
        self.rect.x += x_shift

class Coin(AnimatedTile):
    def __init__(self, size, x, y, path, value) -> None:
        super().__init__(size, x, y, path)
        center_x = x + int(size /2)
        center_y = y + int(size /2)
        self.rect = self.image.get_rect(center = (center_x, center_y))
        self.value = value
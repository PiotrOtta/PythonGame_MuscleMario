from matplotlib import image
import pygame

class UI:
    def __init__(self, surface) -> None:
        
        # inicjalizacja
        self.display_surface = surface

        # zdrowie
        image = pygame.image.load('graphics/ui/health_bar.png').convert_alpha()
        self.health_bar = pygame.transform.scale(image, (300, 140))
        self.health_bar_topleft = (100, 60)
        self.bar_max_width = 175
        self.bar_height = 16

        # monety
        image = pygame.image.load('graphics/ui/coin.png').convert_alpha()
        self.coin = pygame.transform.scale(image, (80, 80))
        self.coin_rect = self.coin.get_rect(topleft = (75, 75))
        self.font = pygame.font.Font(None, 50)

    def show_health(self, current, full):
        self.display_surface.blit(self.health_bar, (0, 0))
        current_health_ratio = current / full
        current_bar_width = self.bar_max_width * current_health_ratio
        health_bar_rect = pygame.Rect(self.health_bar_topleft, (current_bar_width, self.bar_height))
        pygame.draw.rect(self.display_surface, '#fa3232', health_bar_rect)

    def show_coins(self, amount):
        self.display_surface.blit(self.coin, self.coin_rect)
        coin_amount_surf = self.font.render(str(amount), False, 'black')
        coin_amount_rect = coin_amount_surf.get_rect(midleft = (self.coin_rect.right + 3, self.coin_rect.centery))
        self.display_surface.blit(coin_amount_surf, coin_amount_rect)
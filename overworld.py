import pygame
from extender import import_folder
from game_data import levels
from decoration import Sky

class Node(pygame.sprite.Sprite):
    def __init__(self, pos, status, icon_speed, path) -> None:
        super().__init__()
        self.frames = import_folder(path)
        self.frame_index = 0
        image = self.frames[self.frame_index]
        self.image = self.image = pygame.transform.scale(image, (320, 192))
        if status:
            self.status = True
        else:
            self.status = False
        self.rect = self.image.get_rect(center = pos)

        self.detection_zone = pygame.Rect(self.rect.centerx - (icon_speed / 2), self.rect.centery - (icon_speed / 2), icon_speed, icon_speed)
    
    def animate(self):
        self.frame_index += 0.15
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        image = self.frames[int(self.frame_index)]
        self.image = self.image = pygame.transform.scale(image, (320, 192))

    def update(self):
        if self.status:
            self.animate()
        else:
            tint_surf = self.image.copy()
            tint_surf.fill('black', None, pygame.BLEND_RGBA_MULT)
            self.image.blit(tint_surf, (0,0))

class Icon(pygame.sprite.Sprite):
    def __init__(self, pos) -> None:
        super().__init__()
        self.pos = pos
        self.image = pygame.image.load('graphics/overworld/player_icon.png').convert_alpha()
        self.rect = self.image.get_rect(center = pos)

    def update(self):      
        self.rect.center = self.pos

class Overworld:
    def __init__(self, start_level, max_level, surface, create_level) -> None:
        
        # inicjalizacja
        self.display_surface = surface
        self.max_level = max_level
        self.current_level = start_level
        self.create_level = create_level

        # przechodzenie miedzy punktami
        self.move_direction = pygame.math.Vector2(0, 0)
        self.speed = 12
        self.moving = False

        # grafiki
        self.setup_nodes()
        self.setup_icon()
        self.sky = Sky(7, 'overworld')

    def setup_nodes(self):
        self.nodes = pygame.sprite.Group()

        for index, node_data in enumerate(levels.values()):
            if index <= self.max_level:
                node_sprite = Node(node_data['node_pos'], True, self.speed, node_data['node_graphics'])
            else :
                node_sprite = Node(node_data['node_pos'], False, self.speed, node_data['node_graphics'])
            self.nodes.add(node_sprite)
    
    def setup_icon(self):
        self.icon = pygame.sprite.GroupSingle()
        icon_sprite = Icon(self.nodes.sprites()[self.current_level].rect.center)
        self.icon.add(icon_sprite)
        
    def draw_paths(self):
        points = [node['node_pos'] for index, node in enumerate(levels.values()) if index <= self.max_level]
        if len(points) > 1:
            pygame.draw.lines(self.display_surface, 'brown', False, points, 15)

    def input(self):
        keys = pygame.key.get_pressed()

        if not self.moving:
            if keys[pygame.K_RIGHT] and self.current_level < self.max_level:
                self.move_direction = self.get_movement_data(self.current_level + 1)
                self.current_level += 1
                self.moving = True
            elif keys[pygame.K_LEFT] and self.current_level > 0:
                self.move_direction = self.get_movement_data(self.current_level - 1)
                self.current_level -= 1
                self.moving = True
            elif keys[pygame.K_SPACE] or keys[pygame.K_RETURN]:
                self.create_level(self.current_level)
        self.update_icon_pos()
    
    def get_movement_data(self, target):
        start = pygame.math.Vector2(self.nodes.sprites()[self.current_level].rect.center)
        end = pygame.math.Vector2(self.nodes.sprites()[target].rect.center)

        return (end - start).normalize()

    def update_icon_pos(self):
        if self.moving and self.move_direction:
            self.icon.sprite.pos += self.move_direction * self.speed
            target_node = self.nodes.sprites()[self.current_level]
            if target_node.detection_zone.collidepoint(self.icon.sprite.pos):
                self.moving = False
                self.move_direction = pygame.math.Vector2(0, 0)

    def run(self):
        self.input()
        self.icon.update()
        self.nodes.update()

        self.sky.draw(self.display_surface)

        self.draw_paths()
        self.nodes.draw(self.display_surface)
        self.icon.draw(self.display_surface)
from math import sin
import pygame

from extender import import_folder
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, surface, create_jump_particles, change_health) -> None:
        super().__init__()
        self.import_character_assets()
        self.frame_index = 0
        self.animation_speed = 0.15
        self.image = self.animations['idle'][self.frame_index]
        self.rect = self.image.get_rect(topleft = pos)

        # dymek
        self.import_dust_run_particles()
        self.dust_frame_index = 0
        self.dust_animation_speed = 0.15
        self.display_surface = surface
        self.create_jump_particles = create_jump_particles

        # chodzenie i skakanie
        self.direction = pygame.math.Vector2(0, 0)
        self.speed = 10
        self.gravity = 0.8
        self.jump_speed = -18
        self.collision_rect = pygame.Rect(self.rect.topleft, (100, self.rect.height - 30))

        # dźwięki
        self.jump_sound = pygame.mixer.Sound('sounds/jump.mp3')
        self.jump_sound.set_volume(0.1)
        self.hurt_sound = pygame.mixer.Sound('sounds/hurt.mp3')
        self.hurt_sound.set_volume(0.4)

        # statusy gracza
        self.status = 'idle'
        self.attacking = False
        self.facing_right = True
        self.on_ground = False
        self.on_ceiling = False
        self.on_left = False
        self.on_right = False
        self.change_health = change_health
        self.invincible = False
        self.invincibility_duration = 400
        self.hurt_time = 0
    
    def import_character_assets(self):
        character_path = 'graphics/character/'
        self.animations = {
            'idle': [],
            'run': [],
            'jump': [],
            'fall': [],
            'attack': []
            }
        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

    def import_dust_run_particles(self):    
        self.dust_run_particles = import_folder('graphics/character/dust_particles/run')
    
    def animate(self):
        animation = self.animations[self.status]

        self.frame_index += self.animation_speed
        if self.frame_index > len(animation):
            self.frame_index = 0

        image = animation[int(self.frame_index)]
        if self.facing_right:
            self.image = image
            self.rect.bottomleft = self.collision_rect.bottomleft
        else:
            flipped_image = pygame.transform.flip(image, True, False)
            self.image = flipped_image
            self.rect.bottomright = self.collision_rect.bottomright

        if self.invincible:
            alpha = self.wave_value()
            self.image.set_alpha(alpha)
        else:
            self.image.set_alpha(255) 
        
        self.rect = self.image.get_rect(midbottom = self.rect.midbottom)

    def run_dust_animation(self):
        if self.status == 'run' and self.on_ground:
            self.dust_frame_index += self.dust_animation_speed

            if self.dust_frame_index >= len(self.dust_run_particles):
                self.dust_frame_index = 0

            dust_particle = self.dust_run_particles[int(self.dust_frame_index)]

            if self.facing_right:
                pos  = self.rect.bottomleft - pygame.math.Vector2(10, 70)
                self.display_surface.blit(dust_particle, pos)
            else:
                pos  = self.rect.bottomright - pygame.math.Vector2(50, 70)
                flipped_dust_particle = pygame.transform.flip(dust_particle, True, False)
                self.display_surface.blit(flipped_dust_particle, pos)

    def get_input(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] and self.direction.x == 0 and self.on_ground:
            self.attacking = True
        else:
            if keys[pygame.K_RIGHT]:
                self.facing_right = True
                self.direction.x = 1
            elif keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.facing_right = False
            else:
                self.direction.x = 0

            self.attacking = False
            if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
                self.jump()
                self.jump_sound.play()
                self.create_jump_particles(self.rect.midbottom)
    
    def get_status(self):
        if self.attacking:
            self.status = 'attack'
        else:
            if self.direction.y < 0:
                self.status = 'jump'
            elif self.direction.y > 1:
                self.status = 'fall'
            else:
                if self.direction.x != 0:
                    self.status = 'run'
                else:
                    self.status = 'idle'

    def apply_gravity(self):
        self.direction.y += self.gravity
        self.collision_rect.y += self.direction.y
    
    def jump(self):
        self.direction.y = self.jump_speed

    def get_damage(self, level):
        if not self.invincible:
            self.hurt_sound.play()
            self.change_health(-10 * (level > 1 and 1 or level))
            self.invincible = True
            self.hurt_time = pygame.time.get_ticks()

    def invincibility_timer(self):
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.hurt_time >= self.invincibility_duration:
                self.invincible = False
    
    def wave_value(self) -> int:
        value = sin(pygame.time.get_ticks())
        if value >= 0: return 255
        else: return 0
    
    def update(self) -> None:
        self.get_input()
        self.get_status()
        self.animate()
        self.run_dust_animation()
        self.invincibility_timer()
import pygame
from decoration import Clouds, Sky, Water
from enemy import Enemy
from extender import import_csv_layout, import_cut_graphics
from particles import ParticleEffect
from player import Player
from tiles import AnimatedTile, Coin, StaticTile, Tile
from settings import tile_size, screen_width, screen_height
from game_data import levels

class Level:
    def __init__(self, current_level, surface, create_overworld, change_coins, change_health) -> None:
        # ustawienia poziomu
        self.display_surface = surface

        # dźwięki
        self.coin_sound = pygame.mixer.Sound('sounds/coin.mp3')
        self.enemy_death_sound = pygame.mixer.Sound('sounds/enemy_death.mp3')
        self.enemy_death_sound.set_volume(0.4)
        self.fallen_off_sound = pygame.mixer.Sound('sounds/fallen_off.mp3')
        self.fallen_off_sound.set_volume(0.5)

        # połączenie z menu głównym
        level_data = levels[current_level]
        level_content = level_data['content']
        self.current_level = current_level
        self.new_max_level = level_data['unlock']
        self.create_overworld = create_overworld

        self.font = pygame.font.Font(None, 40)
        self.text_surface = self.font.render(level_content, True, 'White')
        self.text_rect = self.text_surface.get_rect(center = (screen_width /2, screen_height / 2))

        # ustawienie gracza
        player_layout = import_csv_layout(level_data['player'])
        self.player = pygame.sprite.GroupSingle()
        self.goal = pygame.sprite.GroupSingle()
        self.player_setup(player_layout, change_health)

        # interfejs
        self.change_coins = change_coins

        # ustawienie tla
        bg_layout = import_csv_layout(level_data['tlo'])
        self.bg_sprites = self.create_tile_group(bg_layout, 'bg')
        # ustawinie terenu
        terrain_layout = import_csv_layout(level_data['terrain'])
        self.terrain_sprites = self.create_tile_group(terrain_layout, 'terrain')
        # ustawinie trawy
        grass_layout = import_csv_layout(level_data['grass'])
        self.grass_sprites = self.create_tile_group(grass_layout, 'grass')
        # ustawinie trawy
        terrain_bg_layout = import_csv_layout(level_data['bg terrain'])
        self.terrain_bg_sprites = self.create_tile_group(terrain_bg_layout, 'terrain_bg')
        # ustawienie monet
        coin_layout = import_csv_layout(level_data['coins'])
        self.coin_sprites = self.create_tile_group(coin_layout, 'coins')
        # ustawienie wrogowie
        enemy_layout = import_csv_layout(level_data['enemy'])
        self.enemy_sprites = self.create_tile_group(enemy_layout, 'enemy')
        # constraints
        constraints_layout = import_csv_layout(level_data['constraints'])
        self.constraints_sprites = self.create_tile_group(constraints_layout, 'constraints')

        # dekoracje
        self.sky = Sky(7)
        level_width = len(terrain_layout[0]) * tile_size
        self.water = Water(screen_height - 120, level_width)
        self.clouds = Clouds(300, level_width, 25)

        self.world_shift = 0

        # dymek
        self.dust_sprite = pygame.sprite.GroupSingle()
        self.explosion_sprites = pygame.sprite.Group()
        self.player_on_ground = False

    def player_setup(self, layout, change_health):
        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                x = col_index * tile_size
                y = row_index * tile_size
                if val == "0":
                    sprite = Player((x, y), self.display_surface, self.create_jump_particles, change_health)
                    self.player.add(sprite)
                if val == "1":
                    surface = pygame.image.load('graphics/goal/goal.png').convert_alpha()
                    sprite = StaticTile(tile_size, x, y, surface)
                    self.goal.add(sprite)

    def create_tile_group(self, layout, type):
        sprite_group = pygame.sprite.Group()

        for row_index, row in enumerate(layout):
            for col_index, val in enumerate(row):
                if val != "-1":
                    x = col_index * tile_size
                    y = row_index * tile_size

                    if type == "bg":
                        bg_tile_list = import_cut_graphics('levels/terrain.png')
                        tile_surface = bg_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    elif type == "terrain":
                        terrain_tile_list = import_cut_graphics('levels/terrain.png')
                        tile_surface = terrain_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    elif type == "grass":
                        grass_tile_list = import_cut_graphics('levels/grass.png')
                        tile_surface = grass_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    elif type == "terrain_bg":
                        terrain_bg_tile_list = import_cut_graphics('levels/bg_terrain.png')
                        tile_surface = terrain_bg_tile_list[int(val)]
                        sprite = StaticTile(tile_size, x, y, tile_surface)
                    elif type == "coins":
                        if val == '0':
                            sprite = Coin(tile_size, x, y, 'graphics/coins/gold/', 10)
                        elif val == '1':
                            sprite = Coin(tile_size, x, y, 'graphics/coins/silver/', 1)
                    elif type == "enemy":
                        sprite = Enemy(tile_size, x, y)
                    elif type == "constraints":
                        sprite = Tile(tile_size, x, y)
                    
                    sprite_group.add(sprite)

        return sprite_group

    def create_jump_particles(self, pos):
        if self.player.sprite.facing_right:
            pos -= pygame.math.Vector2(1, 30)
        else:
            pos += pygame.math.Vector2(1, -30)
        jump_particle_sprite = ParticleEffect(pos, type='jump') 
        self.dust_sprite.add(jump_particle_sprite)   
    
    def get_player_on_ground(self):
        if self.player.sprite.on_ground:
            self.player_on_ground = True
        else:
            self.player_on_ground = False
    
    def create_landing_dust(self):
        if not self.player_on_ground and self.player.sprite.on_ground and not self.dust_sprite:
            if self.player.sprite.facing_right:
                offset = pygame.math.Vector2(0, 25)
            else:
                offset = pygame.math.Vector2(-0, 25)
            fall_dust_particle = ParticleEffect(self.player.sprite.rect.midbottom - offset, 'land')
            self.dust_sprite.add(fall_dust_particle)

    def scroll_x(self):
        player = self.player.sprite
        player_x = player.rect.centerx
        direction_x = player.direction.x

        poziom = screen_width /4
        if player_x < poziom and direction_x < 0:
            self.world_shift = 10
            player.speed = 0
        elif player_x > screen_width - poziom and direction_x > 0:
            self.world_shift = -10
            player.speed = 0
        else:
            self.world_shift = 0
            player.speed = 8

    def horizontal_movement_collision(self):
        player = self.player.sprite
        player.collision_rect.x += player.direction.x * player.speed

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.x < 0:
                    player.collision_rect.left = sprite.rect.right
                    player.on_left = True
                elif player.direction.x > 0:
                    player.collision_rect.right = sprite.rect.left
                    player.on_right = True

    def vertical_movement_collision(self):
        player = self.player.sprite
        player.apply_gravity()

        for sprite in self.terrain_sprites.sprites():
            if sprite.rect.colliderect(player.collision_rect):
                if player.direction.y > 0:
                    player.collision_rect.bottom = sprite.rect.top
                    player.direction.y = 0
                    player.on_ground = True
                elif player.direction.y < 0:
                    player.collision_rect.top = sprite.rect.bottom
                    player.direction.y = 0
                    player.on_ceiling = True
        
        if player.on_ground and player.direction.y < 0 or player.direction.y > 1:
            player.on_ground = False

    def enemy_collision_reverse(self):
        for enemy in self.enemy_sprites.sprites():
            if pygame.sprite.spritecollide(enemy, self.constraints_sprites, False):
                enemy.reverse()
    
    def check_death(self):
        if self.player.sprite.rect.top > screen_height:
            self.create_overworld(self.current_level, 0)
            self.fallen_off_sound.play()

    def check_win(self):
        if pygame.sprite.spritecollide(self.player.sprite, self.goal, False):
            self.create_overworld(self.current_level, self.new_max_level)

    def check_coin_collision(self):
        collided_coins = pygame.sprite.spritecollide(self.player.sprite, self.coin_sprites, True)
        if collided_coins:
            for coin in collided_coins:
                self.change_coins(coin.value)
                self.coin_sound.play()

    def check_enemy_collision(self):
        enemy_collisions = pygame.sprite.spritecollide(self.player.sprite, self.enemy_sprites, False)
        if enemy_collisions:
            for enemy in enemy_collisions:
                if self.player.sprite.attacking:
                    self.kill_the_enemy(enemy)
                else:
                    enemy_center = enemy.rect.centery
                    enemy_top = enemy.rect.top
                    player_bottom = self.player.sprite.rect.bottom
                    if enemy_top < player_bottom < enemy_center and self.player.sprite.direction.y >= 0:
                        self.player.sprite.direction.y = -12
                        self.kill_the_enemy(enemy)
                    else:
                        self.player.sprite.get_damage(self.current_level)
    
    def kill_the_enemy(self, enemy):
        self.enemy_death_sound.play()
        explosion_kill = ParticleEffect(enemy.rect.center, 'explosion')
        self.explosion_sprites.add(explosion_kill)
        enemy.kill()

    def run(self):

        self.display_surface.blit(self.text_surface, self.text_rect)

        # dymek
        # self.create_jump_particles(self.world_shift)
        self.dust_sprite.update(self.world_shift)

        # dekoracje
        self.sky.draw(self.display_surface)
        self.clouds.draw(self.display_surface, self.world_shift)

        # grafika poziomu
        self.bg_sprites.update(self.world_shift)
        self.bg_sprites.draw(self.display_surface)
        self.terrain_bg_sprites.update(self.world_shift)
        self.terrain_bg_sprites.draw(self.display_surface)
        self.terrain_sprites.update(self.world_shift)
        self.terrain_sprites.draw(self.display_surface)
        self.enemy_sprites.update(self.world_shift)
        self.constraints_sprites.update(self.world_shift)

        self.enemy_collision_reverse()
        self.enemy_sprites.draw(self.display_surface)
        self.explosion_sprites.update(self.world_shift)
        self.explosion_sprites.draw(self.display_surface)

        self.grass_sprites.update(self.world_shift)
        self.grass_sprites.draw(self.display_surface)
        self.coin_sprites.update(self.world_shift)
        self.coin_sprites.draw(self.display_surface)
        self.goal.update(self.world_shift)
        self.goal.draw(self.display_surface)

        self.water.draw(self.display_surface, self.world_shift)

        self.scroll_x()

        self.check_death()
        self.check_win()
        self.check_coin_collision()
        self.check_enemy_collision()

        # # gracz
        self.player.update()
        self.horizontal_movement_collision()
        self.get_player_on_ground()
        self.vertical_movement_collision()
        self.create_landing_dust()
        self.player.draw(self.display_surface)
        self.dust_sprite.draw(self.display_surface)
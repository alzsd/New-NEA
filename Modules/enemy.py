import pygame
import os
import math

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
        idle_sheet_path = os.path.join(assets_path, "Enemy_idle.png")
        
        self.idle_sprite_sheet = pygame.image.load(idle_sheet_path).convert_alpha()
        self.image = self.idle_sprite_sheet
        self.rect = self.image.get_rect()
        
        death_sheet_path = os.path.join(assets_path, "Enemy_death.png")
        self.death_sprite_sheet = pygame.image.load(death_sheet_path).convert_alpha()
        
        self.rect.x = x
        self.rect.y = y
        self.world_x = x  # Keep track of world position
        self.world_y = y
        self.health = 100
        self.max_health = 100
        self.x_vel = 0  # Enemy movement speed
        self.y_vel = 0
        self.gravity = 1
        self.is_dying = False
        self.alpha = 255
        
        self.spawn_x = x
        self.patrol_range = 200
        self.patrol_limits = (self.spawn_x - self.patrol_range, self.spawn_x + self.patrol_range)
        self.speed = 1
        self.patrol_direction = 1  # 1 for right, -1 for left
        
        self.is_jumping = False
        self.jump_strength = -15
        self.jump_interval = 120  # Number of frames between jumps
        self.jump_timer = self.jump_interval

        # Load sound effects
        self.move_sound = pygame.mixer.Sound("enemy move.wav")
        self.death_sound = pygame.mixer.Sound("enemy die.wav")
        self.take_damage_sound = pygame.mixer.Sound("enemy damaged.wav")
        
        # Sound flags
        self.move_sound_playing = False
        self.death_sound_playing = False
        self.take_damage_sound_playing = False

    def update(self, platforms, player, scroll_x):
        if not self.is_dying:
            # Check if the player is within patrol range + buffer
            if abs(self.world_x - player.rect.x) <= self.patrol_range + 50:
                self.pursue_player(player)
            else:
                self.patrol()
            
            # Update the world position based on velocity
            self.world_x += self.x_vel
            self.world_y += self.y_vel
            self.y_vel += self.gravity

            self.check_platform_collisions(platforms)

            # Boundary checks to keep enemies within game world bounds
            self.world_x = max(0, min(self.world_x, 5000))  # Example bounds (adjust as necessary)
            self.world_y = max(0, min(self.world_y, 1080))  # Example bounds (adjust as necessary)

            # Calculate distance to the player
            player_pos = player.rect.center
            enemy_pos = self.rect.center
            distance = math.sqrt((player_pos[0] - enemy_pos[0]) ** 2 + (player_pos[1] - enemy_pos[1]) ** 2)

            # Adjust volume based on distance (simple linear function)
            scaling_factor = 0.3
            max_distance = 800  # Maximum distance for hearing the sound
            volume = max(0, min(1, 1 - (distance / max_distance))) * scaling_factor
            self.move_sound.set_volume(volume)
            self.death_sound.set_volume(volume)
            self.take_damage_sound.set_volume(volume)

            # Play movement sound periodically
            if self.rect.x % 100 == 0 and not self.move_sound_playing:
                self.move_sound.play()
                self.move_sound_playing = True
            elif self.rect.x % 100 != 0:
                self.move_sound_playing = False
        else:
            self.fade_out()

        # Update screen position based on world position and scroll_x
        self.rect.x = self.world_x + scroll_x
        self.rect.y = self.world_y



    def check_platform_collisions(self, platforms):
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        
        for platform in collisions:
            # Handle vertical collisions
            if self.y_vel > 0:  # Falling down
                if self.rect.bottom > platform.rect.top and self.rect.bottom - self.y_vel <= platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.world_y = self.rect.y
                    self.y_vel = 0
            elif self.y_vel < 0:  # Jumping up
                if self.rect.top < platform.rect.bottom and self.rect.top - self.y_vel >= platform.rect.bottom:
                    self.rect.top = platform.rect.bottom
                    self.world_y = self.rect.y
                    self.y_vel = 0

            # Handle horizontal collisions
            if self.x_vel > 0:  # Moving right
                if self.rect.right > platform.rect.left and self.rect.right - self.x_vel <= platform.rect.left:
                    self.rect.right = platform.rect.left
                    self.world_x = self.rect.x
                    self.x_vel = 0
            elif self.x_vel < 0:  # Moving left
                if self.rect.left < platform.rect.right and self.rect.left - self.x_vel >= platform.rect.right:
                    self.rect.left = platform.rect.right
                    self.world_x = self.rect.x
                    self.x_vel = 0

    def take_damage(self, amount):
        self.health -= amount+30
        if not self.take_damage_sound_playing:
            self.take_damage_sound.play()
            self.take_damage_sound_playing = True
        if self.health <= 0:
            self.health = 0
            self.start_dying()
            
    def start_dying(self):
        self.is_dying = True
        self.image = self.death_sprite_sheet
        self.alpha = 255
        if not self.death_sound_playing:
            self.death_sound.play()
            self.death_sound_playing = True
            
    def draw(self, surface, scroll_x):
        # Draw enemy based on world position relative to scroll
        surface.blit(self.image, (self.world_x, self.world_y))
        self.draw_health_bar(surface, scroll_x)

    def draw_health_bar(self, surface, scroll_x):
        bar_width = 100
        bar_height = 5
        health_bar_length = bar_width * (self.health / self.max_health)
        
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x , self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x , self.rect.y - 10, health_bar_length, bar_height))

    def fade_out(self):
        self.alpha -= 1
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)
            
    def pursue_player(self, player):
        if self.rect.x < player.rect.x:
            self.x_vel = self.speed
        else:
            self.x_vel = -self.speed
                
    def jump(self):
        self.jump_timer -= 1
        if self.jump_timer <= 0:
            self.jump_timer = self.jump_interval
            if self.rect.x >= self.patrol_limits[1] or self.rect.x <= self.patrol_limits[0]:
                self.patrol_direction *= -1  # Change direction
            self.x_vel = self.patrol_direction * self.speed
            self.y_vel = self.jump_strength
            self.is_jumping = True
        else:
            self.x_vel = self.patrol_direction * self.speed if self.is_jumping else 0
            
    def patrol(self):
        # Patrol between the defined patrol limits
        if self.world_x >= self.patrol_limits[1]:
            self.patrol_direction = -1  # Change direction to left
        elif self.world_x <= self.patrol_limits[0]:
            self.patrol_direction = 1  # Change direction to right
        self.x_vel = self.patrol_direction * self.speed

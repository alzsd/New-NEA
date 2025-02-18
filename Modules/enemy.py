import pygame
import os

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Define the path to the assets folder and the idle sprite sheet
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
        idle_sheet_path = os.path.join(assets_path, "Enemy_idle.png")
        
        # Load the sprite sheet
        self.idle_sprite_sheet = pygame.image.load(idle_sheet_path).convert_alpha()
        # Assign the sprite sheet to self.image
        self.image = self.idle_sprite_sheet
        # Set the rect attribute based on the image
        self.rect = self.image.get_rect()
        
        #death sprite loading
        death_sheet_path = os.path.join(assets_path, "Enemy_death.png")
        self.death_sprite_sheet = pygame.image.load(death_sheet_path).convert_alpha()
        
        self.rect.x = x
        self.rect.y = y
        self.health = 100
        self.max_health = 100
        self.x_vel = 0  # Enemy movement speed
        self.y_vel = 0
        self.gravity = 1
        self.is_dying = False
        self.alpha = 255

    def update(self, *args):
        platforms = args[0]
        
        if not self.is_dying:
            self.rect.x += self.x_vel
            self.rect.y += self.y_vel
            self.y_vel += self.gravity

            # Enemy movement logic (example: moving back and forth)
            if self.rect.right >= 800 or self.rect.left <= 0:
                self.x_vel = -self.x_vel  # Change direction when hitting screen edges

            # Collision detection with platforms
            self.check_platform_collisions(platforms)
        else:
            self.fade_out()

    def check_platform_collisions(self, platforms):
        collisions = pygame.sprite.spritecollide(self, platforms, False)
        if collisions:
            for platform in collisions:
                if self.rect.bottom > platform.rect.top:
                    self.rect.bottom = platform.rect.top
                    self.y_vel = 0

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.start_dying()
            
    def start_dying(self):
        self.is_dying = True
        self.image = self.death_sprite_sheet
        self.alpha = 255
            
    def draw_health_bar(self, surface):
        bar_width = 100
        bar_height = 5
        health_bar_length = bar_width * (self.health / self.max_health)
        
        pygame.draw.rect(surface, (255, 0, 0), (self.rect.x, self.rect.y - 10, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0), (self.rect.x, self.rect.y - 10, health_bar_length, bar_height))
        
    def draw(self, surface):
        surface.blit(self.image, self.rect)
        pygame.draw.rect(surface, (0, 255, 0), self.rect, 1)  # Green box around the enemy

    def fade_out(self):
        self.alpha -=1
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)
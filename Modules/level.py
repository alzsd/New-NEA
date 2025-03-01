import pygame
import os


# Level class
class Level:
    def __init__(self):
        self.platforms = pygame.sprite.Group()
        
    def add_platform(self, platform):
        self.platforms.add(platform)
        
    def draw(self, screen, scroll_x):
        # Draw each platform with scroll_x consideration
        for platform in self.platforms:
            platform.update(scroll_x)  # Update rect positions
            platform.draw(screen)      # Draw without scroll_x parameter
        
    def check_collisions(self, player):
        collisions = pygame.sprite.spritecollide(player, self.platforms, False)
        if collisions:
            for platform in collisions:
                if player.rect.bottom > platform.rect.top:
                    player.rect.bottom = platform.rect.top
                    player.is_jumping = False
                    player.y_vel = 0

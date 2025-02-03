import pygame
import os


# Level class
class Level:
    def __init__(self):
        self.platforms = pygame.sprite.Group()
        
    def add_platform(self, platform):
        self.platforms.add(platform)
        # Adds a new platform to the group
        
    def draw(self, screen):
        self.platforms.draw(screen)
        # Renders all platforms (tiles) with a single draw call
        
    def check_collisions(self, player):
        collisions = pygame.sprite.spritecollide(player, self.platforms, False)  # Checks for collisions between the player and any platforms in the group.
        if collisions:
            for platform in collisions:
                if player.rect.bottom > platform.rect.top:
                    player.rect.bottom = platform.rect.top
                    player.is_jumping = False
                    player.y_vel = 0
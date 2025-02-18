import pygame
import os


# Level class
class Level:
    def __init__(self):
        self.platforms = pygame.sprite.Group()
        
    def add_platform(self, platform):
        self.platforms.add(platform)
        
    def draw(self, screen, scroll_x):
        for platform in self.platforms:
            platform.draw(screen, scroll_x)
        
    def check_collisions(self, player):
        collisions = pygame.sprite.spritecollide(player, self.platforms, False)
        if collisions:
            for platform in collisions:
                if player.rect.bottom > platform.rect.top:
                    player.rect.bottom = platform.rect.top
                    player.is_jumping = False
                    player.y_vel = 0

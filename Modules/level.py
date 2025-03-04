import pygame
import os

# Level class
class Level:
    def __init__(self):
        self.platforms = pygame.sprite.Group()
        self.wood_items = pygame.sprite.Group()  
        
    def add_platform(self, platform):
        self.platforms.add(platform)
        
    def add_wood(self, wood):
        self.wood_items.add(wood)
            
    def update(self, scroll_x):
        for platform in self.platforms:
            platform.update(scroll_x)
        self.wood_items.update(scroll_x)
            
    def draw(self, screen, scroll_x):
        for platform in self.platforms:
            platform.update(scroll_x)
            platform.draw(screen)
        for wood in self.wood_items:
            wood.update(scroll_x)
            wood.draw(screen)
        
    def check_collisions(self, player):
        collisions = pygame.sprite.spritecollide(player, self.platforms, False)
        if collisions:
            for platform in collisions:
                if player.rect.bottom > platform.rect.top:
                    player.rect.bottom = platform.rect.top
                    player.is_jumping = False
                    player.y_vel = 0



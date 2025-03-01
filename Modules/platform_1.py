import pygame
import os

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))  # Correct size tuple
        self.image.fill((0, 50, 0))  # Correct RGB tuple
        self.rect = self.image.get_rect()
        self.world_x = x  # Track world position
        self.world_y = y
        self.rect.x = x
        self.rect.y = y


        
    def update(self, scroll_x):
        # Update rect position based on world position and scroll_x
        self.rect.x = self.world_x - scroll_x
        self.rect.y = self.world_y

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
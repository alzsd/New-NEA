import pygame
import os

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))  # Correct size tuple
        self.image.fill((0, 50, 0))  # Correct RGB tuple
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def draw(self, screen, scroll_x):
        screen.blit(self.image, (self.rect.x + scroll_x, self.rect.y))

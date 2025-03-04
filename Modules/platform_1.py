import pygame
import os

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, type, should_flip=False):
        super().__init__()
        # Set the image path based on the type of platform
        if type == '1':
            self.image = pygame.image.load("tile.png").convert_alpha()
            self.image = pygame.transform.scale(self.image,(1.1*70,64))
        elif type == '2':
            self.image = pygame.image.load("tile2.png").convert_alpha()
            self.image = pygame.transform.scale(self.image,(1.1*70,64))
        if should_flip:
            self.image = pygame.transform.flip(self.image, True, False)  # Flip horizontally

        self.rect = self.image.get_rect()
        self.world_x = x  # Track world position
        self.world_y = y
        self.rect.x = x
        self.rect.y = y

    def update(self, scroll_x):
        # Update rect position based on world position and scroll_x
        self.rect.x = self.world_x + scroll_x
        self.rect.y = self.world_y
        

    def draw(self, screen):
        # Draw the image at the rect's updated position
        screen.blit(self.image, (self.rect.x, self.rect.y))
        #outline_color = (255, 0, 0)  # Red color for the outline
        #outline_thickness = 2  # Thickness of the outline
        #pygame.draw.rect(screen, outline_color, self.rect, outline_thickness)
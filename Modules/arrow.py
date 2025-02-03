import pygame
import os
import math

#arrow class
class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
        arrow_path = os.path.join(assets_path, "Arrow.png")
        self.image = pygame.image.load(arrow_path).convert_alpha() #this links the image file
        
        self.original_image = self.image #keeps track of original direction of the arrow
        self.rect = self.image.get_rect(center = (x, y))
        self.direction = direction
        self.x_vel = 10 if direction == "right" else -10
        self.y_vel = -10 #initial velocity acting upwards
        self.gravity = 0.7
        
    def update(self):
        self.y_vel += self.gravity #simulates gravitational acceleration
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel #changes the next position of the rect
        
        #rotating the image based on its resultant velocity
        angle = math.degrees(math.atan2(-self.y_vel, self.x_vel))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center = self.rect.center)
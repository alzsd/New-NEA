import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((255, 0, 0))  # Red color for the enemy
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.health = 100
        self.x_vel = 0  # Enemy movement speed
        self.y_vel = 0
        self.gravity = 1

    def update(self, *args):
        platforms = args[0]
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        # Enemy movement logic (example: moving back and forth)
        if self.rect.right >= 800 or self.rect.left <= 0:
            self.x_vel = -self.x_vel  # Change direction when hitting screen edges

        # Collision detection with platforms
        self.check_platform_collisions(platforms)

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
            self.kill()

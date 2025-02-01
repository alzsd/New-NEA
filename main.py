# Libraries
import pygame
import os

# Global variables
speed = 3

# Dictionaries for start positions
start_positions = {
   "level1": (50, 300),
   "level2": (50, 300),
   "level3": (50, 300)
}

# Platform class
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))  # Correct size tuple
        self.image.fill((0, 50, 0))  # Correct RGB tuple
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

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

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, screen, max_health):
        super().__init__()
        self.screen = screen
        self.direction = "right"  # Initial direction of sprite
        self.max_health = max_health
        self.health = self.max_health
        
        # Equipment
        self.equipped_weapon = "sword"
        
        # Defining the path to the assets folder
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
       
        # Load sprite sheets for different actions
        run_sheet_path = os.path.join(assets_path, "Link_runs.PNG")
        idle_sheet_path = os.path.join(assets_path, "Link_idle6.PNG")
        jump_sheet_path = os.path.join(assets_path, "Link_jump.PNG")
        sword_attack_sheet_path = os.path.join(assets_path, "Link_sword_attack.PNG")

        self.run_sheet = pygame.image.load(run_sheet_path).convert_alpha()
        self.idle_sheet = pygame.image.load(idle_sheet_path).convert_alpha()
        self.jump_sheet = pygame.image.load(jump_sheet_path).convert_alpha()
        self.sword_attack_sheet = pygame.image.load(sword_attack_sheet_path).convert_alpha()

        # Initialize the rect attribute before calling load_frames
        self.rect = pygame.Rect(0, 0, 0, 0)

        # Load frames for animations
        self.run_frames = self.load_frames(self.run_sheet, num_columns=10)
        self.idle_frames = self.load_frames(self.idle_sheet, num_columns=1)
        self.jump_frames = self.load_frames(self.jump_sheet, num_columns=1)
        self.sword_attack_frames = self.load_frames(self.sword_attack_sheet, num_columns=9)

        # Initial player state
        self.current_frames = self.idle_frames
        self.current_frame_index = 0
        self.image = self.current_frames[self.current_frame_index]
        self.rect.topleft = start_pos

        # Movement and state variables
        self.x_vel = 0
        self.y_vel = 0
        self.is_jumping = False
        self.is_attacking = False  # Track attack state
        self.jump_strength = 15
        self.gravity = 1
        self.frame_count = 0

    def load_frames(self, sprite_sheet, num_columns):
        frames = []
        sheet_width, sheet_height = sprite_sheet.get_size()
        frame_width = sheet_width // num_columns
        frame_height = sheet_height

        for col in range(num_columns):
            x = col * frame_width
            if x + frame_width <= sheet_width:  # Ensure x coordinate is within bounds
                frame = sprite_sheet.subsurface(pygame.Rect(x, 0, frame_width, frame_height - 10))
                frames.append(frame)

        # Adjust the rect size to match the first frame size
        if frames:
            self.rect = frames[0].get_rect()

        return frames

    def update(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity

        # Choose the correct set of frames based on state
        if self.is_attacking:
            self.current_frames = self.sword_attack_frames
        elif self.is_jumping:
            self.current_frames = self.jump_frames
        elif self.x_vel != 0:
            self.current_frames = self.run_frames
            self.direction = "left" if self.x_vel < 0 else "right"
        else:
            self.current_frames = self.idle_frames

        # Update to next frame for animation
        self.frame_count += 1
        if self.frame_count >= 10:
            self.frame_count = 0
            self.current_frame_index = (self.current_frame_index + 1) % len(self.current_frames)
            self.image = self.current_frames[self.current_frame_index]
            # Flipping the image based on direction
            if self.direction == "left":
                self.image = pygame.transform.flip(self.image, True, False)

            # Reset attack state when animation completes
            if self.is_attacking and self.current_frame_index == len(self.sword_attack_frames) - 1:
                self.is_attacking = False

        # Collision detection for borders
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.screen.get_width():
            self.rect.right = self.screen.get_width()
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.screen.get_height():
            self.rect.bottom = self.screen.get_height()
            self.is_jumping = False
            self.y_vel = 0

        # Ensure the player stays above the floor
        self.check_ground_collision()

    # Method to ensure the player collides with the ground
    def check_ground_collision(self):
        if self.rect.bottom > self.screen.get_height() - 50:
            self.rect.bottom = self.screen.get_height() - 50
            self.is_jumping = False
            self.y_vel = 0

    def move_left(self, speed):
        self.x_vel = -speed

    def move_right(self, speed):
        self.x_vel = speed

    def jump(self):
        if not self.is_jumping:
            self.y_vel = -self.jump_strength
            self.is_jumping = True

    def stop(self, enemies):
        self.x_vel = 0
    
    def attack(self):
        if self.equipped_weapon == "sword" and not self.is_attacking:  # Ensure sword is equipped
            self.is_attacking = True
            self.current_frames = self.sword_attack_frames
            self.current_frame_index = 0
            self.frame_count = 0

            """# Check for collisions with enemies
            for enemy in enemies:
                if self.rect.colliderect(enemy.rect):
                    enemy.take_damage(25)  # Adjust damage as needed"""

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.health = 0
            self.die()

    def heal(self, amount):
        self.health += amount
        if self.health > self.max_health:
            self.health = self.max_health

    def draw_health_bar(self, screen):
        # Health bar calibration
        bar_width = 200
        bar_height = 20
        border_colour = (169, 169, 169)
        fill_colour = (0, 255, 0)
        outline_rect = pygame.Rect(10, 10, bar_width, bar_height)
        fill_rect = pygame.Rect(10, 10, bar_width * (self.health / self.max_health), bar_height)

        # Drawing the border
        pygame.draw.rect(screen, border_colour, outline_rect, 2)
        # Drawing the filling
        pygame.draw.rect(screen, fill_colour, fill_rect)

    def draw_health_text(self, screen):
        font = pygame.font.SysFont(None, 24)
        health_text = font.render(f'{self.health} / {self.max_health}', True, (255, 255, 255))
        screen.blit(health_text, (10, 35))  # Position below the health bar

# Handle input function
def handle_input(player):
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.move_left(3)  # Adjust speed as needed
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.move_right(3)  # Adjust speed as needed
    else:
        player.stop()

    if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
        player.jump()
    
    # Handle mouse input for attack
    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0] and player.equipped_weapon == "sword":  # Left mouse button for sword attack
        player.attack()
    
    # Handle weapon switching
    if keys[pygame.K_1]:
        player.equipped_weapon = "sword"

# Start level function
def start_level(level_name, screen, difficulty):
    start_pos = start_positions[level_name]
    
    #setting max_health based on desired difficulty setting
    if difficulty == "easy":
        max_health = 150
    elif difficulty == "medium":
        max_health = 100
    else:  # hard
        max_health = 75
    
    player = Player(start_pos, screen, max_health)
    return player


# Main initialiser
def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Fullscreen mode
    clock = pygame.time.Clock()

    #set the difficulty level
    difficulty = "medium"
    
    # Create the test level
    test_level = Level()

    # Add floor platforms with a hole
    for x in range(0, 500, 100):  # Adding ground platforms with a gap (hole)
        test_level.add_platform(Platform(x, screen.get_height() - 50, 100, 50))
    for x in range(600, screen.get_width(), 100):  # Continue platforms after the hole
        test_level.add_platform(Platform(x, screen.get_height() - 50, 100, 50))

    # Add floating platforms based on my example image
    test_level.add_platform(Platform(300, screen.get_height() - 200, 100, 20))
    test_level.add_platform(Platform(500, screen.get_height() - 300, 100, 20))

    current_level = "level1"
    player = start_level(current_level, screen, difficulty)
    character_sprites = pygame.sprite.Group()
    character_sprites.add(player)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        handle_input(player)
        character_sprites.update()
        test_level.check_collisions(player)

        screen.fill((0, 0, 0))
        test_level.draw(screen)  # Draw the test level platforms
        character_sprites.draw(screen)
        
        player.draw_health_bar(screen)
        player.draw_health_text(screen)
        
        pygame.display.flip()
        clock.tick(120)

    pygame.quit()

if __name__ == "__main__":
    main()

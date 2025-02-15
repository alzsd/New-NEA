import pygame
import os
import math

#arrow class
class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
        arrow_path = os.path.join(assets_path, "Arrow_4.png")
        self.image = pygame.image.load(arrow_path).convert_alpha() #this links the image file
        #self.image = pygame.transform.scale(self.image, int(self.image.get_width()*0.2 ), int(self.image.get_height()*0.2))
        
        self.original_image = self.image #keeps track of original direction of the arrow
        self.rect = self.image.get_rect(center = (x, y))
        self.direction = direction
        self.x_vel = 10 if direction == "right" else -10
        self.y_vel = -10 #initial velocity acting upwards
        self.gravity = 0.2
        
        self.timer = 0  # Initialise a timer to track arrow lifespan
        
    def update(self):
        self.y_vel += self.gravity #simulates gravitational acceleration
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel #changes the next position of the rect
        
        #rotating the image based on its resultant velocity
        angle = math.degrees(math.atan2(-self.y_vel, self.x_vel))
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center = self.rect.center)
        
        self.timer += 1/120 # assuming my game will run at 120 fps
        
        if self.timer > 0.5: #setting a time limit
            print(f"Arrow killed - lifespan exceeded {self.timer}")
            self.kill() #removes the arrow from the existing sprite group

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, screen, max_health):
        super().__init__()
        self.screen = screen
        self.direction = "right"  # Initial direction of sprite
        self.max_health = max_health
        self.health = self.max_health
        self.equipped_weapon = "bow"
        
        #keep track of arrow shooting spritesheet:
        self.shooting_timer = 0.0
        self.shooting_duration = 0.4
                
        #bow cooldown attributes:
        self.shooting_cooldown = 1.0
        self.last_shot_time = 0.0
        self.shooting = False # This merely tracks the shooting state!
        
        # Defining the path to the assets folder
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
       
        # Load sprite sheets for different actions
        run_sheet_path = os.path.join(assets_path, "Link_runs.PNG")
        idle_sheet_path = os.path.join(assets_path, "Link_idle6.PNG")
        jump_sheet_path = os.path.join(assets_path, "Link_jump.PNG")
        bow_sheet_path = os.path.join(assets_path, "Link_bow_attack.png")

        self.run_sheet = pygame.image.load(run_sheet_path).convert_alpha()
        self.idle_sheet = pygame.image.load(idle_sheet_path).convert_alpha()
        self.jump_sheet = pygame.image.load(jump_sheet_path).convert_alpha()
        self.bow_sheet = pygame.image.load(bow_sheet_path).convert_alpha()

        # Initialize the rect attribute before calling load_frames
        self.rect = pygame.Rect(0, 0, 0, 0)

        # Load frames for animations
        self.run_frames = self.load_frames(self.run_sheet, num_columns=10)
        self.idle_frames = self.load_frames(self.idle_sheet, num_columns=1)
        self.jump_frames = self.load_frames(self.jump_sheet, num_columns=1)
        self.bow_frames = self.load_frames(self.bow_sheet, num_columns=1)

        # Initial player state
        self.current_frames = self.idle_frames
        self.current_frame_index = 0
        self.image = self.current_frames[self.current_frame_index]
        self.rect.topleft = start_pos

        # Movement and state variables
        self.x_vel = 0
        self.y_vel = 0
        self.is_jumping = False
        self.jump_strength = 15
        self.gravity = 1
        self.frame_count = 0

        #arrow group
        self.arrows = pygame.sprite.Group()

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

    def attack(self):
        if self.equipped_weapon == "bow": #and not self.shooting
            self.shooting = True  # Set to True when attack starts
            self.current_frames = self.bow_frames

    def shoot_arrow(self):
        if self.equipped_weapon == "bow":
            print("shooting arrow - !Debug!")
            direction = self.direction
            arrow = Arrow(self.rect.centerx, self.rect.centery, direction)
            self.arrows.add(arrow)



    def update(self):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        
        self.arrows.update()
        
        if self.shooting:
            self.shooting_timer -= 1 / 120  # Assuming 120 FPS
            if self.shooting_timer <= 0:
                self.shooting = False

        # Choose the correct set of frames based on state
        if self.shooting and self.equipped_weapon == "bow":
            self.current_frames = self.bow_frames
            self.direction = "left" if self.x_vel < 0 else "right"
            
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

    def stop(self):
        self.x_vel = 0

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
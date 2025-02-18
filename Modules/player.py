import pygame
import os
import math
MAX_ARROW_SPEED = 15
MAX_DISPLACEMENT = 600

#arrow class
class Arrow(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, aim_angle,speed):
        super().__init__()
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
        arrow_path = os.path.join(assets_path, "Arrow_7.png")
        self.image = pygame.image.load(arrow_path).convert_alpha() #this links the image file
        
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * 3), int(self.image.get_height() * 1.5)))

        
        self.original_image = self.image #keeps track of original direction of the arrow
        
        self.rect = self.image.get_rect(center = (x, y))
        self.aim_angle = aim_angle
        self.speed = speed
        
        self.direction = direction
        self.x_vel = self.speed * math.cos(self.aim_angle)
        self.y_vel = self.speed * math.sin(self.aim_angle) #initial velocity acting upwards
        self.gravity = 0.2
        
        self.timer = 0  # Initialise a timer to track arrow lifespan
        self.stuck = False  # Flag to check if the arrow is stuck
        self.alpha = 255  # Opacity for fading
        
        
    def update(self, enemies, platforms, screen_width, screen_height):
        if not self.stuck:
            self.y_vel += self.gravity #simulates gravitational acceleration
            self.rect.x += self.x_vel
            self.rect.y += self.y_vel #changes the next position of the rect
            
            #rotating the image based on its resultant velocity
            angle = math.degrees(math.atan2(-self.y_vel, self.x_vel))
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center = self.rect.center)
            
            self.timer += 1/120 # assuming my game will run at 120 fps
            
            if self.timer > 1: #setting a time limit
                print(f"Arrow killed - lifespan exceeded {self.timer}")
                self.kill() #removes the arrow from the existing sprite group
                
            #print(f"Arrow position: {self.rect.topleft}")

            hit_enemies = pygame.sprite.spritecollide(self, enemies, False)
            for enemy in hit_enemies:
                print(f"Arrow hit enemy at position: {enemy.rect.topleft}")
                print(f"Arrow hit enemy at position: {enemy.rect.topleft}, size: {enemy.rect.size}")
                enemy.take_damage(10)
                self.kill()
                
            hit_platforms = pygame.sprite.spritecollide(self, platforms, False)
            if hit_platforms or self.rect.left < 0 or self.rect.right > screen_width or self.rect.top < 0 or self.rect.bottom > screen_height:
                self.stuck = True
        
        else:
            # Fade away
            self.alpha -= 5  # Adjust fading speed as needed
            if self.alpha <= 0:
                self.kill()
            else:
                self.image.set_alpha(self.alpha)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        pygame.draw.rect(surface, (0, 255, 0), self.rect, 1)  # Green box around the arrow




    
# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, screen, max_health,speed):
        super().__init__()
        self.screen = screen
        self.direction = "right"  # Initial direction of sprite
        self.max_health = max_health
        self.health = self.max_health
        self.equipped_weapon = "bow"
        self.speed = speed  # Updated the speed for calculating trajectory
        
        # Keep track of arrow shooting spritesheet:
        self.shooting_timer = 0.0
        self.shooting_duration = 0.4
        self.damage_cooldown = 0  # Cooldown time tracker
        self.damage_cooldown_duration = 5*120  # Sets cooldown time
                
        # Bow cooldown attributes:
        self.shooting_cooldown = 1.0
        self.last_shot_time = 0.0
        self.shooting = False  # This merely tracks the shooting state!
        self.trajectory = []  # To store the trajectory points
        
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

        # Scale the sprite sheets
        self.run_sheet = pygame.transform.scale(self.run_sheet, (int(self.run_sheet.get_width() * 1.2), int(self.run_sheet.get_height() * 1.5)))
        self.idle_sheet = pygame.transform.scale(self.idle_sheet, (int(self.idle_sheet.get_width() * 1.2), int(self.idle_sheet.get_height() * 1.5)))
        self.jump_sheet = pygame.transform.scale(self.jump_sheet, (int(self.jump_sheet.get_width() * 1.2), int(self.jump_sheet.get_height() * 1.5)))
        self.bow_sheet = pygame.transform.scale(self.bow_sheet, (int(self.bow_sheet.get_width() * 1.2), int(self.bow_sheet.get_height() * 1.5)))


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

        # Arrow group
        self.arrows = pygame.sprite.Group()
        
    def draw(self, screen, scroll_x):
        screen.blit(self.image, (self.rect.x + scroll_x, self.rect.y))

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
        if self.equipped_weapon == "bow":
            self.shooting = True  # Set to True when attack starts
            self.current_frames = self.bow_frames

    def shoot_arrow(self):
        if self.equipped_weapon == "bow":
            print("shooting arrow - !Debug!")
            direction = self.direction
            arrow_speed = self.calculate_arrow_speed(pygame.mouse.get_pos())
            arrow = Arrow(self.rect.centerx, self.rect.centery, direction, self.aim_angle, arrow_speed)
            self.arrows.add(arrow)


    def calculate_trajectory(self, speed, gravity=0.2, num_points=30):
        self.trajectory = []
        t = 0
        interval = 1.2  # Time interval between points
        for _ in range(num_points):
            t += interval
            x = self.rect.centerx + speed * t * math.cos(self.aim_angle)
            y = self.rect.centery + speed * t * math.sin(self.aim_angle) + 0.5 * gravity * t ** 2
            self.trajectory.append((x, y))
            #print(f"Trajectory: {self.trajectory}")  # Debug line


    def draw_trajectory(self, scroll_x):
        #print("drawing trajectory...")
        for point in self.trajectory:
            pygame.draw.circle(self.screen, (127, 127, 127), (int(point[0] + scroll_x), int(point[1])), 3)  # Grey color for the trajectory

    def clear_trajectory(self):
        self.trajectory = [] # no points = no trajectory shown anymore



    def update(self, enemies, platforms, screen_width, screen_height, scroll_x):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        
        # Decrementing the damage cooldown timer
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        # Ensure the arrows update with the new arguments
        self.arrows.update(enemies, platforms, screen_width, screen_height)
        
        if self.shooting:
            self.shooting_timer -= 1 / 120  # Assuming 120 FPS
            if self.shooting_timer <= 0:
                self.shooting = False

        # Choose the correct set of frames based on state
        if self.shooting and self.equipped_weapon == "bow":
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
        
        # Draw the trajectory if the player is aiming
        if self.shooting:
            self.draw_trajectory(scroll_x)


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
        if self.damage_cooldown == 0:  # Check if cooldown is zero
            print(f"Taking damage -{amount}")  # Debug line
            self.health -= amount
            self.damage_cooldown = self.damage_cooldown_duration  # Reset cooldown
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
        
        
    def aim_bow(self, mouse_pos):
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        self.aim_angle = math.atan2(dy, dx)
        print(f"aim_angle: {self.aim_angle}")  # Debug line
        
        # Flip the bow frames if the mouse is to the left of the player
        if dx < 0:
            self.current_frames = [pygame.transform.flip(frame, True, False) for frame in self.bow_frames]
            self.direction = "left"
            print("Flipped bow frames to the left")
        else:
            self.current_frames = self.bow_frames
            self.direction = "right"
            print("Bow frames to the right")
        
        speed = self.calculate_arrow_speed(mouse_pos)
        self.calculate_trajectory(speed)

        
        
    def die(self):
        print("player has died!")
        #more here later on

    def calculate_arrow_speed(self, mouse_pos):
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        displacement = math.sqrt(dx**2 + dy**2) #pythagorean theorem
        if displacement > MAX_DISPLACEMENT:
            displacement = MAX_DISPLACEMENT
        return (displacement / MAX_DISPLACEMENT) * MAX_ARROW_SPEED


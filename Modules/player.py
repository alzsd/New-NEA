import pygame
import os
import math
MAX_ARROW_SPEED = 15
MAX_DISPLACEMENT = 600

#arrow class
# Arrow class
class Arrow(pygame.sprite.Sprite):
    arrow_sound_playing = False  # Class variable to track the arrow sound state

    def __init__(self, x, y, direction, aim_angle, speed, damage):
        super().__init__()
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
        arrow_path = os.path.join(assets_path, "Arrow_7.png")
        self.image = pygame.image.load(arrow_path).convert_alpha()  # This links the image file
        
        self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * 2.2), int(self.image.get_height()*0.8)))
        self.damage = damage
        
        self.original_image = self.image  # Keeps track of original direction of the arrow
        
        self.rect = self.image.get_rect(center=(x, y))
        self.aim_angle = aim_angle
        self.speed = speed
        
        self.direction = direction
        self.x_vel = self.speed * math.cos(self.aim_angle)
        self.y_vel = self.speed * math.sin(self.aim_angle)  # Initial velocity acting upwards
        self.gravity = 0.2
        
        self.timer = 0  # Initialise a timer to track arrow lifespan
        self.stuck = False  # Flag to check if the arrow is stuck
        self.alpha = 255  # Opacity for fading

    def update(self, enemies, platforms, screen_width, screen_height, arrow_platform):
        if not self.stuck:
            self.y_vel += self.gravity  # Simulates gravitational acceleration
            self.rect.x += self.x_vel
            self.rect.y += self.y_vel  # Changes the next position of the rect
            
            # Rotating the image based on its resultant velocity
            angle = math.degrees(math.atan2(-self.y_vel, self.x_vel))
            self.image = pygame.transform.rotate(self.original_image, angle)
            self.rect = self.image.get_rect(center=self.rect.center)
            
            self.timer += 1 / 120  # Assuming my game will run at 120 fps
            
            hit_enemies = pygame.sprite.spritecollide(self, enemies, False)
            for enemy in hit_enemies:
                print(f"Arrow hit enemy at position: {enemy.rect.topleft}")
                enemy.take_damage(self.damage)
                self.kill()
                
            hit_platforms = pygame.sprite.spritecollide(self, platforms, False)
            if hit_platforms or self.rect.left < 0 or self.rect.right > screen_width or self.rect.top < 0 or self.rect.bottom > screen_height:
                self.stuck = True
        else:
            # Play arrow hit platform sound if not already playing
            if not Arrow.arrow_sound_playing:
                arrow_platform.play()
                Arrow.arrow_sound_playing = True
            
            # Fade away
            self.alpha -= 5  # Adjust fading speed as needed
            if self.alpha <= 0:
                self.kill()
                Arrow.arrow_sound_playing = False  # Reset the flag when the arrow is removed
            else:
                self.image.set_alpha(self.alpha)
                
    def draw(self, surface,screen):
        surface.blit(self.image, self.rect)
        outline_color = (255, 0, 0)  # Red color for the outline
        outline_thickness = 2  # Thickness of the outline
        pygame.draw.rect(screen,outline_color, self.rect, outline_thickness)


def apply_strength_powerup(player):
    for arrow in player.arrows:
        arrow.damage *= 2



# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, start_pos, screen, max_health,speed,powerup_group):
        super().__init__()
        self.screen = screen
        self.direction = "right"  # Initial direction of sprite
        self.max_health = max_health
        self.health = self.max_health
        self.equipped_weapon = "bow"
        self.speed = speed# Updated the speed for calculating trajectory
        self.original_speed = speed
        self.speed_timer = 5*120
        self.strength_timer = 5*120  # Initialize strength timer
        self.has_strength_powerup = False  # Track if strength power-up is active
        self.powerup_group = powerup_group
        self.damage = 10
        self.is_invincible = False  # Add invincibility attribute
        self.invincible_timer = 0  # Add invincibility timer attribute
        
        self.cooldown = 1600  # Cooldown time in milliseconds (3 seconds)
        self.last_shot_time = 0
        
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
        self.run_sheet = pygame.transform.scale(self.run_sheet, (int(self.run_sheet.get_width()*1.1), int(self.run_sheet.get_height()*1.1)))
        self.idle_sheet = pygame.transform.scale(self.idle_sheet, (int(self.idle_sheet.get_width()*1.1), int(self.idle_sheet.get_height()*1.1)))
        self.jump_sheet = pygame.transform.scale(self.jump_sheet, (int(self.jump_sheet.get_width()*1.1), int(self.jump_sheet.get_height()*1.1)))
        self.bow_sheet = pygame.transform.scale(self.bow_sheet, (int(self.bow_sheet.get_width()*1.1), int(self.bow_sheet.get_height()*1.1)))


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
        self.active_powerups = []  # List to store active power-ups
        self.dead = False

        
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

    def shoot_arrow(self,player_shoot_sound):
        current_time = pygame.time.get_ticks()
        if self.equipped_weapon == "bow" and current_time - self.last_shot_time >= self.cooldown:
            player_shoot_sound.play()
            print("shooting arrow - !Debug!")
            direction = self.direction
            arrow_speed = self.calculate_arrow_speed(pygame.mouse.get_pos())
            damage = 50 if self.has_strength_powerup else 10  # Double the damage if strength power-up is active
            print(f"Arrow damage: {damage}")  # Debug
            arrow = Arrow(self.rect.centerx, self.rect.centery, direction, self.aim_angle, arrow_speed,damage)
            self.arrows.add(arrow)
            self.last_shot_time = current_time  # Update the last shot time

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


    def draw_trajectory(self):
        #print("drawing trajectory...")
        for point in self.trajectory:
            pygame.draw.circle(self.screen, (127, 127, 127), (int(point[0]), int(point[1])), 3)  # Grey color for the trajectory

    def clear_trajectory(self):
        self.trajectory = [] # no points = no trajectory shown anymore



    def update(self, enemies, platforms, screen_width, screen_height, scroll_x,player_powerup_sound,arrow_platform):
        self.rect.x += self.x_vel
        self.rect.y += self.y_vel
        self.y_vel += self.gravity
        
        # Decrementing the damage cooldown timer
        if self.damage_cooldown > 0:
            self.damage_cooldown -= 1
        
        # Ensure the arrows update with the new arguments
        self.arrows.update(enemies, platforms, screen_width, screen_height,arrow_platform)
        
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
            self.draw_trajectory()
            
        # Handle speed boost timer
        if self.speed_timer > 0:
            self.speed_timer -= 1
            if self.speed_timer <= 0:
                self.speed = self.original_speed
                # Deactivate speed power-up
                self.deactivate_powerup("speed")
        
        # Handle strength power-up timer
        if self.strength_timer > 0:
            self.strength_timer -= 1
            if self.strength_timer <= 0:
                self.has_strength_powerup = False
                # Deactivate strength power-up
                self.deactivate_powerup("strength")
                
        # Handle invincibility timer
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.is_invincible = False
                # Deactivate invincibility power-up
                self.deactivate_powerup("godmode")
                
        powerup_collisions = pygame.sprite.spritecollide(self,self.powerup_group,True)
        if powerup_collisions:
            for powerup in powerup_collisions:
                player_powerup_sound.play()
                self.power_up(powerup)


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

    def take_damage(self, amount,damage):
        
        if self.damage_cooldown == 0 and not self.is_invincible:  # Check if cooldown is zero
            print(f"Taking damage -{amount}")  # Debug line
            damage.play()
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
        #player_aimbow_sound.play()
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
        self.dead = True

    def calculate_arrow_speed(self, mouse_pos):
        dx = mouse_pos[0] - self.rect.centerx
        dy = mouse_pos[1] - self.rect.centery
        displacement = math.sqrt(dx**2 + dy**2) #pythagorean theorem
        if displacement > MAX_DISPLACEMENT:
            displacement = MAX_DISPLACEMENT
        return (displacement / MAX_DISPLACEMENT) * MAX_ARROW_SPEED
    

        
                
    def power_up(self,powerup):
        powerup.apply_effect(self)
        
    def check_powerup_collisions(self):
        powerup_collisions = pygame.sprite.spritecollide(self, self.powerup_group, True)
        if powerup_collisions:
            for powerup in powerup_collisions:
                self.power_up(powerup)
                
    # Method to update active power-ups
    def update_active_powerups(self):
        for powerup in self.powerup_group:
            if powerup.active:
                if powerup not in self.active_powerups:
                    self.active_powerups.append(powerup)
            else:
                if powerup in self.active_powerups:
                    self.active_powerups.remove(powerup)
                    
    def deactivate_powerup(self, powerup_type):
        for powerup in self.active_powerups:
            if powerup.type == powerup_type:
                powerup.active = False
                self.active_powerups.remove(powerup)
                break
                        
    
        
class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.original_x = x
        self.original_y = y
        self.type = powerup_type
        self.active = False  # Add active status

        powerup_images = {
            "health": "health_powerup.png",
            "speed": "speed_powerup.png",
            "strength": "strength_powerup.png",
            "godmode": "defense_powerup.png"
        }

        try:
            if powerup_type in powerup_images:
                image_path = os.path.join(os.path.dirname(__file__), "Assets", powerup_images[powerup_type])
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (int(0.7 * 50), int(0.7 * 63)))
            else:
                raise ValueError(f"Unknown power-up type: {powerup_type}")
        except FileNotFoundError:
            print(f"Warning: {powerup_images[powerup_type]} not found. Using default image.")
            self.image = pygame.Surface((20, 20))
            self.image.fill((255, 255, 0))

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def apply_effect(self, player):
        # Application logic for power-ups remains the same
        if self.type == "health":
            self.active = True
            player.heal(50)
        elif self.type == "speed":
            self.active = True
            player.speed += 3
            player.speed_timer = 5 * 120
        elif self.type == "strength":
            self.active = True
            player.has_strength_powerup = True
            player.strength_timer = 5 * 120
        elif self.type == "godmode":  # Handle defense power-up
            self.active = True
            player.is_invincible = True
            player.invincible_timer = 5 * 120  # 5 seconds at 120 FPS
        self.active = True  # Set power-up as active when applied

    def update(self, scroll_x):
        # Positioning with respect to world coordinates
        self.rect.x = self.original_x + scroll_x
        self.rect.y = self.original_y

    def draw(self, surface):
        surface.blit(self.image, self.rect)




class Wood(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        assets_path = os.path.join(os.path.dirname(__file__), "Assets")
        wood_path = os.path.join(assets_path, "wood.png")  # Ensure you have a wood.png file in your Assets folder
        self.image = pygame.image.load(wood_path).convert_alpha()  # Load the image for the wood item
        self.image = pygame.transform.scale(self.image,(50,63))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)  # Position the wood item at the given coordinates
        self.original_x = x
        self.original_y = y

    def update(self, scroll_x):
        # Update position based on scroll
        self.rect.x = self.original_x+scroll_x

    def draw(self, screen):
        # Draw the wood item on the screen
        screen.blit(self.image, self.rect)
        
class HUD:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 24)  # Smaller font size for HUD text
        # Box color is a darker grey (here a tuple with no alpha, since pygame.draw.rect ignores alpha)
        self.box_color = (80, 80, 80)
        self.shadow_color = (0, 0, 0)          # Black shadow
        self.box_rect = pygame.Rect(10, screen.get_height() - 80, 240, 60)
        self.text = self.font.render("Active Powerups", True, (0, 0, 0))  # Label in black
        self.text_rect = self.text.get_rect(topleft=(15, screen.get_height() - 75))

    def draw(self, player):
        # Draw the shadow, then the box
        shadow_rect = self.box_rect.move(2, 2)
        pygame.draw.rect(self.screen, self.shadow_color, shadow_rect, border_radius=10)
        pygame.draw.rect(self.screen, self.box_color, self.box_rect, border_radius=10)
        self.screen.blit(self.text, self.text_rect)

        # Dictionary mapping powerup types to their corresponding image filename
        powerup_images = {
            "health": "health_powerup.png",
            "speed": "speed_powerup.png",
            "strength": "strength_powerup.png",
            "godmode": "defense_powerup.png"
        }

        x_offset = 20
        for powerup_type, image_filename in powerup_images.items():
            image_path = os.path.join(os.path.dirname(__file__), "Assets", image_filename)
            powerup_image = pygame.image.load(image_path).convert_alpha()
            powerup_image = pygame.transform.scale(powerup_image, (30, 30))

            # Use the active_powerups list to check if this type is active
            if any(p.type == powerup_type for p in player.active_powerups):
                powerup_image.set_alpha(255)  # Fully opaque if active
            else:
                powerup_image.set_alpha(153)  # Translucent (60% opacity) if inactive

            self.screen.blit(powerup_image, (x_offset, self.screen.get_height() - 50))
            x_offset += 40








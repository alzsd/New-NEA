import pygame
import os
import math
import time
from Modules import Player, Platform, Level, Arrow, Enemy, PowerUp

#sound effects
pygame.mixer.init()
#loading sound effects
player_powerup_sound = pygame.mixer.Sound("powerup.mp3")
#player_aimbow_sound = pygame.mixer.Sound("aim bow.mp3")
player_shoot_sound = pygame.mixer.Sound("shoot bow.mp3")
player_running = pygame.mixer.Sound("running.mp3")
player_running.set_volume(0.2)
ambience = pygame.mixer.Sound("ambience.mp3")
Player_jump = pygame.mixer.Sound("jump.wav")
Player_jump.set_volume(0.2)
damage = pygame.mixer.Sound("damage.wav")
damage.set_volume(0.5)
arrow_platform = pygame.mixer.Sound("arrow hits platform.wav")
arrow_platform.set_volume(0.4)
menu_sound = pygame.mixer.Sound("menu_sound.wav")

enemy_move_sound = pygame.mixer.Sound("enemy move.wav")
enemy_death_sound = pygame.mixer.Sound("enemy die.wav")
enemy_take_damage_sound = pygame.mixer.Sound("enemy damaged.wav")



# Global variables/constants
speed = 3
WORLD_WIDTH = 4000  # May change
player_start_x = 50
player_start_y = 300

running_sound_playing = False
jumping_sound_playing = False
arrow_sound_playing = False
menu_sound_playing = False

# Dictionaries for start positions
start_positions = {
   "level1": (player_start_x, player_start_y),
   "level2": (player_start_x, player_start_y),
   "level3": (player_start_x, player_start_y)
}

# Handle input function
def handle_input(player):
    global running_sound_playing, jumping_sound_playing  # Ensure access to the global variables

    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position    

    # Disable movement if the player is shooting
    if player.shooting:
        player.stop()  # Ensure the player stops moving when shooting
        if running_sound_playing:
            player_running.stop()
            running_sound_playing = False
        if jumping_sound_playing:
            Player_jump.stop()
            jumping_sound_playing = False
    else:
        player.x_vel = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if not running_sound_playing:
                player_running.play(-1)  # Loop the sound
                running_sound_playing = True
            player.move_left(player.speed)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if not running_sound_playing:
                player_running.play(-1)  # Loop the sound
                running_sound_playing = True
            player.move_right(player.speed)
        else:
            if running_sound_playing:
                player_running.stop()
                running_sound_playing = False
        
        # Handle jumping independently of movement
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if not jumping_sound_playing:
                Player_jump.play()
                jumping_sound_playing = True
            player.jump()
        else:
            if jumping_sound_playing:
                Player_jump.stop()
                jumping_sound_playing = False
        
        if keys[pygame.K_2]:
            player.equipped_weapon = "bow"
        elif not (keys[pygame.K_LEFT] or keys[pygame.K_a] or keys[pygame.K_RIGHT] or keys[pygame.K_d]):
            player.stop()

    # Call aim_bow to update the aim_angle only if LMB is held down
    if mouse_buttons[0]:
        player.aim_bow(mouse_pos)
        print("aim_bow called")  # Debug line

    # Handle shooting state
    if mouse_buttons[0] and player.equipped_weapon == "bow":
        if not player.shooting:
            player.shooting = True
            player.shooting_timer = player.shooting_duration  # Start the timer
    elif not mouse_buttons[0] and player.shooting:
        print(f"Mouse button released. Equipped weapon: {player.equipped_weapon}")  # Debug line
        if player.equipped_weapon == "bow":
            player.shoot_arrow(player_shoot_sound)
        player.shooting = False
        player.clear_trajectory()  # removes trajectory
        
# Start level function
def start_level(level_name, screen, difficulty, powerup_group):
    start_pos = start_positions[level_name]
    
    # Setting max_health based on desired difficulty setting
    if difficulty == "easy":
        max_health = 150
    elif difficulty == "medium":
        max_health = 125
    else:  # hard
        max_health = 75
    
    player = Player(start_pos, screen, max_health, speed, powerup_group)
    return player

def draw_rounded_rect(screen, color, rect, corner_radius):
    """
    Draw a rounded rectangle.
    """
    pygame.draw.rect(screen, color, rect, border_radius=corner_radius)

def render_pause_menu(screen, formatted_time):
    screen_width, screen_height = screen.get_size()
    
    menu_width = 7 * 96
    menu_height = 6 * 96
    menu_x = (screen_width - menu_width) // 2
    menu_y = (screen_height - menu_height) // 2
    
    shadow_color = (0, 0, 0, 100)
    shadow_rect = pygame.Rect(menu_x + 10, menu_y + 10, menu_width, menu_height)
    pygame.draw.rect(screen, shadow_color, shadow_rect, border_radius=20)
    
    menu_color = (50, 50, 50)
    menu_rect = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
    draw_rounded_rect(screen, menu_color, menu_rect, corner_radius=20)
    
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)
    
    pause_text = font.render("Paused", True, (255, 255, 255))
    time_text = small_font.render(f"Time spent: {formatted_time}", True, (255, 255, 255))
    resume_text = font.render("Resume", True, (255, 255, 255))
    settings_text = font.render("Settings", True, (255, 255, 255))
    quit_text = font.render("Quit", True, (255, 255, 255))
    
    resume_button_rect = resume_text.get_rect(center=(menu_x + menu_width // 2, menu_y + 200))
    settings_button_rect = settings_text.get_rect(center=(menu_x + menu_width // 2, menu_y + 300))
    quit_button_rect = quit_text.get_rect(center=(menu_x + menu_width // 2, menu_y + 400))
    
    screen.blit(pause_text, (menu_x + 20, menu_y + 20))
    screen.blit(time_text, (menu_x + menu_width - time_text.get_width() - 20, menu_y + 20))
    screen.blit(resume_text, resume_button_rect.topleft)
    screen.blit(settings_text, settings_button_rect.topleft)
    screen.blit(quit_text, quit_button_rect.topleft)

    pygame.display.flip()

    return resume_button_rect, settings_button_rect, quit_button_rect

def render_settings_menu(screen, background_image, from_pause_menu):
    screen_width, screen_height = screen.get_size()
    
    # Draw the background image
    screen.blit(background_image, (0, 0))
    
    # Add text and buttons
    font = pygame.font.Font(None, 74)
    small_font = pygame.font.Font(None, 50)
    
    settings_text = font.render("Settings", True, (255, 255, 255))
    controls_text = small_font.render("Controls:", True, (255, 255, 255))
    move_right_text = small_font.render("D / Right Arrow: Move Right", True, (255, 255, 255))
    move_left_text = small_font.render("A / Left Arrow: Move Left", True, (255, 255, 255))
    jump_text = small_font.render("Space / Up Arrow: Jump", True, (255, 255, 255))
    pause_text = small_font.render("ESC: Pause", True, (255, 255, 255))

    # Calculate positions
    settings_x = screen_width - settings_text.get_width() - 20
    settings_y = 20
    controls_y_start = 200
    controls_x = 20

    # Render text
    screen.blit(settings_text, (settings_x, settings_y))
    screen.blit(controls_text, (controls_x, controls_y_start))
    screen.blit(move_right_text, (controls_x, controls_y_start + 50))
    screen.blit(move_left_text, (controls_x, controls_y_start + 100))
    screen.blit(jump_text, (controls_x, controls_y_start + 150))
    screen.blit(pause_text, (controls_x, controls_y_start + 200))

    # Draw the back button (curved arrow)
    back_button_text = small_font.render("<-", True, (255, 255, 255))
    back_button_rect = back_button_text.get_rect(bottomright=(screen_width - 20, screen_height - 20))
    screen.blit(back_button_text, back_button_rect.topleft)

    pygame.display.flip()

    return back_button_rect

# Main initialiser
def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    #play ambience in a loop.
    ambience.play(-1)
    ambience.set_volume(0.3)
    global menu_sound_playing
    
    # Load the background images
    background_image = pygame.image.load("BG1.jpg").convert()
    settings_background_image = pygame.image.load("BG2.jpg").convert()
    settings_background_image = pygame.transform.scale(settings_background_image, (1920, 1080))

    # Define the world width for the extended game map
    WORLD_WIDTH = 5000
    difficulty = "medium"

    # Create the test level
    test_level = Level()

    # Add floor platforms with a hole
    for x in range(0, 500, 100):
        test_level.add_platform(Platform(x, screen.get_height() - 50, 100, 60))
    for x in range(600, WORLD_WIDTH, 100):
        test_level.add_platform(Platform(x, screen.get_height() - 50, 100, 100))

    # Add floating platforms
    test_level.add_platform(Platform(300, screen.get_height() - 200, 100, 20))
    test_level.add_platform(Platform(500, screen.get_height() - 300, 100, 20))

    current_level = "level1"
    # Create a group for power-ups and add some power-ups
    powerup_group = pygame.sprite.Group()
    powerup_group.add(PowerUp(400, screen.get_height() - 130, "health"))
    powerup_group.add(PowerUp(500, screen.get_height() - 360, "speed"))
    powerup_group.add(PowerUp(700, screen.get_height() - 130, "strength"))
    powerup_group.add(PowerUp(2000, screen.get_height() - 130, "godmode"))

    player = start_level(current_level, screen, difficulty, powerup_group)
    character_sprites = pygame.sprite.Group()
    character_sprites.add(player)

    # Creating and adding enemies
    enemies = pygame.sprite.Group()
    enemy = Enemy(300, 930)
    enemy2 = Enemy(1000, 930)
    enemies.add(enemy)
    enemies.add(enemy2)

    running = True
    paused = False
    in_settings = False
    start_time = time.time()  # Initialize start time
    paused_start_time = 0
    total_paused_duration = 0
    
    resume_button_rect = pygame.Rect(0, 0, 1, 1)
    settings_button_rect = pygame.Rect(0, 0, 1, 1)
    quit_button_rect = pygame.Rect(0, 0, 1, 1)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if in_settings:
                        in_settings = False
                    else:
                        paused = not paused
                        if paused:
                            paused_start_time = time.time()
                        else:
                            total_paused_duration += time.time() - paused_start_time

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if paused and not in_settings:
                    if resume_button_rect.collidepoint(mouse_pos):
                        paused = False
                        total_paused_duration += time.time() - paused_start_time
                    elif settings_button_rect.collidepoint(mouse_pos):
                        in_settings = True
                    elif quit_button_rect.collidepoint(mouse_pos):
                        running = False

                if in_settings:
                    back_button_rect = render_settings_menu(screen, settings_background_image, True)
                    if back_button_rect.collidepoint(mouse_pos):
                        in_settings = False
                
                print(f"Mouse button {event.button} pressed at {event.pos}")

        if not paused and not in_settings:
            handle_input(player)
            
            scroll_x = -player.rect.centerx + screen.get_width() // 2
            scroll_x = max(-(WORLD_WIDTH - screen.get_width()), min(0, scroll_x))
            
            character_sprites.update(enemies, test_level.platforms, screen.get_width(), screen.get_height(), scroll_x,player_powerup_sound,arrow_platform)
            
            for enemy in enemies:
                enemy.update(test_level.platforms, player, scroll_x)
                enemy.draw(screen, scroll_x)
            for powerup in powerup_group:
                powerup.update(scroll_x)
                powerup.draw(screen)
            for platform in test_level.platforms:
                platform.update(scroll_x)
                platform.draw(screen)

            test_level.check_collisions(player)

            if pygame.sprite.spritecollideany(player, enemies):
                player.take_damage(10,damage)

            player.check_powerup_collisions()
            
            screen.blit(background_image, (0, 0))
            test_level.draw(screen, scroll_x)
            character_sprites.draw(screen)
            enemies.draw(screen)
            powerup_group.draw(screen)
            
            for enemy in enemies:
                enemy.draw_health_bar(screen, scroll_x)

            player.draw_trajectory()
            player.arrows.draw(screen)
            player.draw_health_bar(screen)
            player.draw_health_text(screen)
            
            pygame.display.flip()
            clock.tick(120)
            time_spent = time.time() - start_time - total_paused_duration
            formatted_time = time.strftime("%M:%S", time.gmtime(time_spent))
        elif paused and not in_settings:
            resume_button_rect, settings_button_rect, quit_button_rect = render_pause_menu(screen, formatted_time)
        elif in_settings:
            paused = False
            back_button_rect = render_settings_menu(screen, settings_background_image, True)

    pygame.quit()


if __name__ == "__main__":
    main()

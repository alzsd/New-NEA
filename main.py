import pygame
import os
import math
import time
from Modules import Player, Platform, Level, Arrow, Enemy, PowerUp, Wood
from pygame import gfxdraw

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
speed = 2
WORLD_WIDTH = 1500000  # May change
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

def render_settings_menu(screen, background_image, ambience_music_volume, sfx_volume):
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
    ambience_music_text = small_font.render(f"Ambience & Music: {int(ambience_music_volume * 100)}%", True, (255, 255, 255))
    sfx_text = small_font.render(f"Sound Effects: {int(sfx_volume * 100)}%", True, (255, 255, 255))

    # Calculate positions
    settings_x = screen_width - settings_text.get_width() - 20
    settings_y = 20
    controls_y_start = 100  # Moved higher up
    controls_x = 20

    # Render text for controls
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

    # Function to draw sliders with knobs and outlines
    def draw_slider_with_knob(x, y, width, height, fill_width, color):
        # Draw the black outline
        pygame.draw.rect(screen, (0, 0, 0), (x - 2, y - 2, width + 4, height + 4))
        # Draw the slider background
        pygame.draw.rect(screen, (255, 255, 255), (x, y, width, height))
        # Draw the filled part of the slider
        pygame.draw.rect(screen, color, (x, y, fill_width, height))
        # Draw the knob as a circle
        knob_radius = height // 2
        knob_x = x + fill_width
        knob_y = y + knob_radius
        pygame.draw.circle(screen, (255, 255, 255), (knob_x, knob_y), knob_radius)
        pygame.draw.circle(screen, (0, 0, 0), (knob_x, knob_y), knob_radius, 2)  # Black outline for the knob

    # Render and position the sliders and their labels to fit within the squares
    screen.blit(ambience_music_text, (50, 600))  # Adjusted y-coordinate for text
    ambience_music_slider_width = 300
    ambience_music_slider_fill = int(ambience_music_volume * ambience_music_slider_width)
    draw_slider_with_knob(50, 650, ambience_music_slider_width, 20, ambience_music_slider_fill, (255, 0, 0))

    screen.blit(sfx_text, (50, 750))  # Adjusted y-coordinate for text
    sfx_slider_width = 300
    sfx_slider_fill = int(sfx_volume * sfx_slider_width)
    draw_slider_with_knob(50, 800, sfx_slider_width, 20, sfx_slider_fill, (0, 0, 255))

    pygame.display.flip()

    return back_button_rect, pygame.Rect(50, 650, 300, 20), pygame.Rect(50, 800, 300, 20)


def draw_rounded_button(screen, rect, color, radius, shadow_offset=5):
    x, y, width, height = rect

    # Draw shadow
    shadow_color = (0, 0, 0)
    shadow_rect = (x + shadow_offset, y + shadow_offset, width, height)
    pygame.gfxdraw.filled_polygon(screen, [
        (shadow_rect[0], shadow_rect[1] + radius),
        (shadow_rect[0], shadow_rect[1] + height - radius),
        (shadow_rect[0] + radius, shadow_rect[1] + height),
        (shadow_rect[0] + width - radius, shadow_rect[1] + height),
        (shadow_rect[0] + width, shadow_rect[1] + height - radius),
        (shadow_rect[0] + width, shadow_rect[1] + radius),
        (shadow_rect[0] + width - radius, shadow_rect[1]),
        (shadow_rect[0] + radius, shadow_rect[1]),
    ], shadow_color)
    
    # Draw button
    pygame.gfxdraw.filled_polygon(screen, [
        (x, y + radius),
        (x, y + height - radius),
        (x + radius, y + height),
        (x + width - radius, y + height),
        (x + width, y + height - radius),
        (x + width, y + radius),
        (x + width - radius, y),
        (x + radius, y),
    ], color)
    pygame.gfxdraw.aapolygon(screen, [
        (x, y + radius),
        (x, y + height - radius),
        (x + radius, y + height),
        (x + width - radius, y + height),
        (x + width, y + height - radius),
        (x + width, y + radius),
        (x + width - radius, y),
        (x + radius, y),
    ], color)


def main_menu(screen):
    # Load the background image
    background_image = pygame.image.load("BG4.jpg").convert()
    background_image = pygame.transform.scale(background_image, (1920, 1080))
    
    # Define button properties
    button_width = 200
    button_height = 50
    button_color = (75, 75, 75)  # Greyish black
    text_color = (255, 255, 255)
    radius = 10  # Radius for rounded corners
    
    # Calculate button positions
    screen_width, screen_height = screen.get_size()
    play_button_rect = pygame.Rect((screen_width - button_width) // 2, screen_height // 2 - button_height - 10, button_width, button_height)
    quit_button_rect = pygame.Rect((screen_width - button_width) // 2, screen_height // 2 + 10, button_width, button_height)
    
    # Initialize fonts
    font = pygame.font.Font(None, 36)
    
    # Render the main menu
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if play_button_rect.collidepoint(mouse_pos):
                    return True  # Start the game
                elif quit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    return False

        # Draw the background image
        screen.blit(background_image, (0, 0))
        
        # Draw the buttons with rounded corners and shadow
        draw_rounded_button(screen, play_button_rect, button_color, radius)
        draw_rounded_button(screen, quit_button_rect, button_color, radius)
        
        # Add text to buttons
        play_text = font.render("Play", True, text_color)
        quit_text = font.render("Quit", True, text_color)
        screen.blit(play_text, play_text.get_rect(center=play_button_rect.center))
        screen.blit(quit_text, quit_text.get_rect(center=quit_button_rect.center))
        
        pygame.display.flip()

    return False

def setup_level(level_layout):
    level = Level()
    tile_size = 50  # Assume each tile is 50x50 pixels

    for row_index, row in enumerate(level_layout):
        for col_index, tile in enumerate(row):
            x = col_index * tile_size
            y = row_index * tile_size
            
            if tile in ['1', '2']:
                should_flip = False
                if tile == '1':
                    if col_index > 0 and level_layout[row_index][col_index - 1] in ['1', '2']:
                        should_flip = True
                    if col_index < len(row) - 1 and level_layout[row_index][col_index + 1] in ['1', '2']:
                        should_flip = False

                platform = Platform(x, y, tile, should_flip)
                level.add_platform(platform)

            
            elif tile == '3':  # Add wood item
                wood = Wood(x, y)
                level.add_wood(wood)
                
    return level



def handle_collect_wood(player, level, screen):
    collected_woods = pygame.sprite.spritecollide(player, level.wood_items, True)
    if collected_woods:
        print(f"Collected {len(collected_woods)} wood items.")
        if not level.wood_items:
            mission_complete(screen)




def mission_complete(screen):
    print("Mission Complete!")
    
    # Mute all audio
    pygame.mixer.music.stop()
    for channel in range(pygame.mixer.get_num_channels()):
        pygame.mixer.Channel(channel).stop()
    
    # Load level complete sound
    level_complete_sound = pygame.mixer.Sound("level complete.mp3")
    level_complete_sound.play()

    # Display "Mission Success"
    font = pygame.font.Font(None, 120)
    text = font.render("Mission Success", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    
    shadow_font = pygame.font.Font(None, 122)
    shadow_text = shadow_font.render("Mission Success", True, (0, 0, 0))
    shadow_text_rect = shadow_text.get_rect(center=(screen.get_width() // 2 + 2, screen.get_height() // 2 + 2))
    
    # Freeze the game and display text
    for alpha in range(255, -1, -5):
        screen.fill((0, 0, 0))
        shadow_text.set_alpha(alpha)
        text.set_alpha(alpha)
        screen.blit(shadow_text, shadow_text_rect)
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.delay(50)
    
    # Return to the main menu
    main_menu(screen)


def draw_wood_collection_bar(screen, collected_woods, total_woods):
    bar_width = 300
    bar_height = 20
    bar_x = (screen.get_width() - bar_width) // 2
    bar_y = 20
    
    proportion_collected = collected_woods / total_woods
    
    # Colors
    bar_color = (255, 215, 0)  # Yellow/Gold color
    border_color = (0, 0, 0)   # Black for the border
    
    # Background bar
    pygame.draw.rect(screen, border_color, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4), border_radius=10)
    pygame.draw.rect(screen, bar_color, (bar_x, bar_y, bar_width * proportion_collected, bar_height), border_radius=10)
    
    # Text
    font = pygame.font.Font(None, 36)
    text = font.render(f"{collected_woods}/{total_woods} woods collected", True, (255, 255, 255))
    text_rect = text.get_rect(center=(screen.get_width() // 2, bar_y + bar_height + 20))
    
    screen.blit(text, text_rect)





# Main initialiser
def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    clock = pygame.time.Clock()
    # Show the main menu
    if not main_menu(screen):
        return  # Exit the game if quit is selected

    # Initialize volume controls
    ambience_music_volume = 0.5  # Default volume for ambience and music
    sfx_volume = 0.5  # Default volume for sound effects

    # Load ambience and music sound
    ambience = pygame.mixer.Sound("ambience.mp3")
    ambience.play(-1)
    ambience.set_volume(ambience_music_volume)
    
    global menu_sound_playing
    
    # Load the background images
    background_image = pygame.image.load("BG1.jpg").convert()
    settings_background_image = pygame.image.load("BG2.jpg").convert()
    settings_background_image = pygame.transform.scale(settings_background_image, (1920, 1080))

    # Define the world width for the extended game map
    WORLD_WIDTH = 9000
    difficulty = "medium"

    # Create the test level
    level_layout = [
        '................................................................................................................................................',
        '................................................................................................................................................',
        '................................................................................................................................................',
        '................................................................................................................................................',
        '................................................................................................................................................',
        '................................................................................................................................................',
        '................................................................................................................................................',
        '................................................................................................................................................',
        '................................................................................................................................................',
        '................................................................................................................................................',
        '................................................................................................................................................',
        '...............................................................................................................................................',
        '.......3....................11111111111........................111111111............................................................................',
        '....111111111......................22221111.........11111...................................................................................................',
        '........................11111........222222222111111111222221................................................................................................',
        '..................111.................2222222222222222222221.......................................................................................',
        '................................................2222222222221.....................................................................................',
        '.............3........1111111.........................222222211111111111111111...................................................................................',
        '..........11111111..........22.........................222222222222........................................................................',
        '........1122222222...........22..............................222222.............................................................................',
        '111111112222222222............22..............................222222.....222222..................................................',
        '2222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222222'          
    ] #each step up is +55 px
    test_level = setup_level(level_layout)
    current_level = "level1"
    # Create a group for power-ups and add some power-ups
    powerup_group = pygame.sprite.Group()
    powerup_group.add(PowerUp(1700, screen.get_height() - 85, "health")) 
    powerup_group.add(PowerUp(600, screen.get_height() - 220, "speed"))
    powerup_group.add(PowerUp(300, screen.get_height() - 470, "speed"))
    powerup_group.add(PowerUp(700, screen.get_height() - 600, "strength"))
    powerup_group.add(PowerUp(2000, screen.get_height() - 130, "godmode"))
    

    player = start_level(current_level, screen, difficulty, powerup_group)
    character_sprites = pygame.sprite.Group()
    character_sprites.add(player)

    # Creating and adding enemies
    enemies = pygame.sprite.Group()
    enemy = Enemy(200, 890)
    enemy2 = Enemy(1200, 930)
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
    back_button_rect = pygame.Rect(0, 0, 1, 1)  # Initialize back button rect for settings menu
    ambience_music_slider_rect = pygame.Rect(0, 0, 1, 1)
    sfx_slider_rect = pygame.Rect(0, 0, 1, 1)

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
                elif in_settings:
                    if back_button_rect.collidepoint(mouse_pos):
                        in_settings = False  # Close settings menu
                    elif ambience_music_slider_rect.collidepoint(mouse_pos):
                        ambience_music_volume = (mouse_pos[0] - ambience_music_slider_rect.x) / ambience_music_slider_rect.width
                        ambience_music_volume = min(max(ambience_music_volume, 0), 1)
                        ambience.set_volume(ambience_music_volume)  # Set ambience and music volume
                    elif sfx_slider_rect.collidepoint(mouse_pos):
                        sfx_volume = (mouse_pos[0] - sfx_slider_rect.x) / sfx_slider_rect.width
                        sfx_volume = min(max(sfx_volume, 0), 1)
                        # Set sound effects volume for all sound effects
                        player_powerup_sound.set_volume(sfx_volume)
                        player_shoot_sound.set_volume(sfx_volume)
                        player_running.set_volume(sfx_volume)  
                        Player_jump.set_volume(sfx_volume)
                        damage.set_volume(sfx_volume)
                        arrow_platform.set_volume(sfx_volume)
                        enemy_move_sound.set_volume(sfx_volume)
                        enemy_death_sound.set_volume(sfx_volume)
                        enemy_take_damage_sound.set_volume(sfx_volume)
                print(f"Mouse button {event.button} pressed at {event.pos}")

        if not paused and not in_settings:
            if menu_sound_playing:
                menu_sound.stop()
                menu_sound_playing = False

            handle_input(player)
            
            scroll_x = -player.rect.centerx + screen.get_width() // 2
            scroll_x = max(-(WORLD_WIDTH - screen.get_width()), min(0, scroll_x))
            
            character_sprites.update(enemies, test_level.platforms, screen.get_width(), screen.get_height(), scroll_x, player_powerup_sound, arrow_platform)
            
            for enemy in enemies:
                enemy.update(test_level.platforms, player, scroll_x)
                enemy.draw(screen, scroll_x)
            for powerup in powerup_group:
                powerup.update(scroll_x)
                powerup.draw(screen)
                


            test_level.check_collisions(player)
            test_level.update(scroll_x)
            test_level.draw(screen, scroll_x)

            if pygame.sprite.spritecollideany(player, enemies):
                player.take_damage(30, damage)

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
            
            handle_collect_wood(player,test_level,screen)
            collected_woods = 5 - len(test_level.wood_items)
            handle_collect_wood(player, test_level, screen)
            
            # Draw HUD
            draw_wood_collection_bar(screen, collected_woods, 5)
            
            pygame.display.flip()
            clock.tick(120)
            time_spent = time.time() - start_time - total_paused_duration
            formatted_time = time.strftime("%M:%S", time.gmtime(time_spent))
        elif paused and not in_settings:
            resume_button_rect, settings_button_rect, quit_button_rect = render_pause_menu(screen, formatted_time)
        elif in_settings:
            paused = False
            back_button_rect, ambience_music_slider_rect, sfx_slider_rect = render_settings_menu(screen, settings_background_image, ambience_music_volume, sfx_volume)

    pygame.quit()

if __name__ == "__main__":
    main()

# Libraries
import pygame
import os
import math
from Modules import Player
from Modules import Platform
from Modules import Level
from Modules import Arrow
from Modules import Enemy
#from Modules import Arrow

# Global variables
speed = 3
#MAX_ARROW_SPEED = 15
#MAX_DISPLACEMENT = 600

# Dictionaries for start positions
start_positions = {
   "level1": (50, 300),
   "level2": (50, 300),
   "level3": (50, 300)
}

# Handle input function
def handle_input(player):
    keys = pygame.key.get_pressed()
    mouse_buttons = pygame.mouse.get_pressed()
    mouse_pos = pygame.mouse.get_pos()  # Get the current mouse position    

    # Disable movement if the player is shooting
    if player.shooting:
        player.stop()  # Ensure the player stops moving when shooting
    else:
        player.x_vel = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.move_left(speed)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.move_right(speed)
        
        # Handle jumping independently of movement
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            player.jump()
        
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
            player.shoot_arrow()
        player.shooting = False
        player.clear_trajectory()  # removes trajectory

            
            
# Start level function
def start_level(level_name, screen, difficulty):
    start_pos = start_positions[level_name]
    
    #setting max_health based on desired difficulty setting
    if difficulty == "easy":
        max_health = 150
    elif difficulty == "medium":
        max_health = 125
    else:  # hard
        max_health = 75
    
    player = Player(start_pos, screen, max_health,speed)
    return player


# Main initialiser
def main():
    pygame.init()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)  # Fullscreen mode
    clock = pygame.time.Clock()

    # Set the difficulty level
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

    # Creating and adding enemies
    enemies = pygame.sprite.Group()
    enemy = Enemy(player.rect.x, player.rect.y)  # Enemy spawns at the player's starting position
    enemies.add(enemy)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # I will use this to debug my current issue -- !resolved!
                print(f"Mouse button {event.button} pressed at {event.pos}")

        handle_input(player)  
        character_sprites.update(enemies, test_level.platforms, screen.get_width(), screen.get_height())
        enemies.update(test_level.platforms)  # Pass platforms to update method

        # Check for collisions between player and platforms
        test_level.check_collisions(player)

        # Check for collisions between player and enemies
        if pygame.sprite.spritecollideany(player, enemies):
            player.take_damage(10)  # Example: player takes damage upon collision

        screen.fill((50, 50, 100))
        
        player.draw_trajectory()
        test_level.draw(screen)  # Draw the test level platforms
        character_sprites.draw(screen)
        enemies.draw(screen)  # Draw the enemies
        
        player.arrows.draw(screen)
        player.draw_health_bar(screen)
        player.draw_health_text(screen)
        
        # Draw health bars for enemies
        for enemy in enemies:
            #enemy.draw(screen)
            enemy.draw_health_bar(screen)
            
        #for arrow in player.arrows:
            #arrow.draw(screen)

        pygame.display.flip()
        clock.tick(120)

    pygame.quit()

if __name__ == "__main__":
    main()


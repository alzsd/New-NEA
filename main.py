# Libraries
import pygame
import os
from Modules import Player
from Modules import Platform
from Modules import Level
from Modules import Arrow
#from Modules import Arrow

# Global variables
speed = 3

# Dictionaries for start positions
start_positions = {
   "level1": (50, 300),
   "level2": (50, 300),
   "level3": (50, 300)
}

# Handle input function
def handle_input(player):
    keys = pygame.key.get_pressed()
    player.x_vel = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.move_left(speed)
    elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.move_right(speed)
    

    elif keys[pygame.K_SPACE] or keys[pygame.K_UP]:
        player.jump()
    
    elif keys[pygame.K_2]:
        player.equipped_weapon = "bow"
        
    else:
        player.stop()

    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0] and not player.shooting:  # Left mouse button is pressed
        player.shooting = True
    elif not mouse_buttons[0] and player.shooting:
        print(f"Mouse button released. Equipped weapon: {player.equipped_weapon}")  # Debugging assistance
        if player.equipped_weapon == "bow":
            player.shoot_arrow()
        player.shooting = False
        
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
    
    player = Player(start_pos, screen, max_health)
    return player


# Main initializer
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
        character_sprites.update()
        player.update(test_level.platforms)  # Ensure platforms group is passed
        test_level.check_collisions(player)

        screen.fill((50, 50, 100))
        test_level.draw(screen)  # Draw the test level platforms
        character_sprites.draw(screen)

        # Update arrows with platform collisions
        player.arrows.update(test_level.platforms)  # Ensure platforms group is passed

        player.arrows.draw(screen)
        player.draw_health_bar(screen)
        player.draw_health_text(screen)
        
        pygame.display.flip()
        clock.tick(120)

    pygame.quit()

if __name__ == "__main__":
    main()

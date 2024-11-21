"""
Snake Eater
Made with PyGame
"""
import threading
import numpy as np
import pygame, sys, time, random, cv2
import VisualRecognition

#Shared variable to stop both camera feed and game loop
stop_event = threading.Event()

direction = 'RIGHT'
change_to = [direction]

# Start the camera in a separate thread
camera_thread = threading.Thread(target=VisualRecognition.run_camera, args=(stop_event, change_to))
camera_thread.start()


# Difficulty settings
# Bigger number is faster snek
difficulty = 2

# Window size
frame_size_x = 720
frame_size_y = 480

# Checks for errors encountered
check_errors = pygame.init()
# pygame.init() example output -> (6, 0)
# second number in tuple gives number of errors
if check_errors[1] > 0:
    print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
    sys.exit(-1)
else:
    print('[+] Game successfully initialised')


# Initialise game window
pygame.display.set_caption('Snake Eater')
game_window = pygame.display.set_mode((frame_size_x, frame_size_y))


# Colors (R, G, B)
black = pygame.Color(0, 0, 0)
white = pygame.Color(255, 255, 255)
red = pygame.Color(255, 0, 0)
green = pygame.Color(0, 255, 0)
blue = pygame.Color(0, 0, 255)


# FPS (frames per second) controller
fps_controller = pygame.time.Clock()


# Game variables
snake_pos = [100, 50]
snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]

food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
food_spawn = True

score = 0


# Game Over
def game_over():

    my_font = pygame.font.SysFont('times new roman', 90)
    game_over_surface = my_font.render('YOU DIED', True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.midtop = (frame_size_x/2, frame_size_y/4)
    game_window.fill(black)
    game_window.blit(game_over_surface, game_over_rect)
    show_score(0, red, 'times', 20)
    pygame.display.flip()
    time.sleep(2)
    stop_event.set()
    pygame.quit()
    sys.exit()


# Score
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, pygame.Color(255, 255, 0) )
    score_rect = score_surface.get_rect()
    if choice == 1:
        score_rect.midtop = (frame_size_x/10, 15)
    else:
        score_rect.midtop = (frame_size_x/2, frame_size_y/1.25)
    game_window.blit(score_surface, score_rect)
    # pygame.display.flip()

##IMAGE THING
background_image = pygame.image.load('menubackground.png')
background_image = pygame.transform.scale(background_image, (frame_size_x, frame_size_y))

# Main logic
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            stop_event.set()
            pygame.quit()
            sys.exit()
        # Whenever a key is pressed down
        elif event.type == pygame.KEYDOWN:
            # W -> Up; S -> Down; A -> Left; D -> Right
            if event.key == pygame.K_UP or event.key == ord('w'):
                change_to[0] = 'UP'
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                change_to[0] = 'DOWN'
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                change_to[0] = 'LEFT'
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                change_to[0] = 'RIGHT'
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    # Making sure the snake cannot move in the opposite direction instantaneously
    if change_to[0] == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to[0] == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to[0] == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to[0] == 'RIGHT' and direction != 'LEFT':
        direction = 'RIGHT'

    # Moving the snake
    if direction == 'UP':
        snake_pos[1] -= 10
    if direction == 'DOWN':
        snake_pos[1] += 10
    if direction == 'LEFT':
        snake_pos[0] -= 10
    if direction == 'RIGHT':
        snake_pos[0] += 10

    # Snake body growing mechanism
    snake_body.insert(0, list(snake_pos))
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score += 1
        difficulty += 1
        food_spawn = False
    else:
        snake_body.pop()

    # Spawning food on the screen
    if not food_spawn:
        food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
    food_spawn = True

    # GFX
    # game_window.fill(black)
    # Draw the background image
    game_window.blit(background_image, (0, 0))

    #Draw the snake head
    pygame.draw.rect(game_window, pygame.Color(255, 255, 255), pygame.Rect(snake_body[0][0]-1, snake_body[0][1]-1, 12, 12))
    pygame.draw.rect(game_window, pygame.Color(255, 223, 0), pygame.Rect(snake_body[0][0], snake_body[0][1], 10, 10))
    #Draw the rest of the snake body
    for pos in snake_body[1:]:
        pygame.draw.rect(game_window, pygame.Color(255, 255, 255), pygame.Rect(pos[0]-1, pos[1]-1, 12, 12))
        pygame.draw.rect(game_window, pygame.Color(249, 239, 172), pygame.Rect(pos[0], pos[1], 10, 10))


    # Snake food
    # pygame.draw.rect(game_window, pygame.Color(249, 239, 172), pygame.Rect(food_pos[0]-1, food_pos[1]-1, 12, 12))
    pygame.draw.rect(game_window, pygame.Color(249, 249, 176), pygame.Rect(food_pos[0]-1, food_pos[1]-1, 12, 12))
    pygame.draw.rect(game_window, pygame.Color(0, 41, 106), pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    # Game Over conditions
    # Getting out of bounds
    if snake_pos[0] < 0 or snake_pos[0] > frame_size_x-10:
        game_over()
    if snake_pos[1] < 0 or snake_pos[1] > frame_size_y-10:
        game_over()
    # Touching the snake body
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:
            game_over()

    #Call the funcs in VisualRecognition.py
    #Obtain head and body pixel coordinates
    head_position, food_position = VisualRecognition.find_snake_positions(game_window)
    #Display coordinates on the game window
    VisualRecognition.show_snake_positions(game_window, head_position, food_position)

    show_score(1, white, 'consolas', 20)
    # Refresh game screen
    pygame.display.update()
    # Refresh rate
    fps_controller.tick(difficulty)
"""
Snake Eater
Made with PyGame
"""
import threading
import numpy as np
import pygame, sys, time, random, cv2

# Shared variable to stop both camera feed and game loop
stop_camera = False

def run_camera():
    global stop_camera, change_to
    cap = cv2.VideoCapture(0)

    while not stop_camera:
        ret, frame = cap.read()
        if ret:
            # Flip the image horizontally to coincide with real-life movements
            frame = cv2.flip(frame, 1)  # 1 means horizontal flip

            # Convert to HSV color space
            hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

            # Define the color range for skin tone
            lower_green = np.array([0, 48, 80], dtype=np.uint8)
            upper_green = np.array([20, 255, 255], dtype=np.uint8)

            # Create a mask for green colors
            mask = cv2.inRange(hsv_frame, lower_green, upper_green)

            # Get the dimensions of the frame
            height, width = frame.shape[:2]

            # Divide the frame into four regions (north, south, east, west)
            north_region = mask[:height//2, :]
            south_region = mask[height//2:, :]
            west_region = mask[:, :width//2]
            east_region = mask[:, width//2:]

            # Count green pixels in each region
            north_pixels = cv2.countNonZero(north_region)
            south_pixels = cv2.countNonZero(south_region)
            west_pixels = cv2.countNonZero(west_region)
            east_pixels = cv2.countNonZero(east_region)

            # Determine the direction with the most green pixels
            max_pixels = max(north_pixels, south_pixels, west_pixels, east_pixels)
            if max_pixels > 0:  # Only change direction if there's a significant amount of green detected
                if max_pixels == north_pixels:
                    change_to = 'UP'
                elif max_pixels == south_pixels:
                    change_to = 'DOWN'
                elif max_pixels == west_pixels:
                    change_to = 'LEFT'
                elif max_pixels == east_pixels:
                    change_to = 'RIGHT'

            # Change the color of green pixels to red (for visualization)
            segmented_frame = frame.copy()
            segmented_frame[mask != 0] = [0, 0, 255]  # Change green pixels to red

            # Display the segmented frame
            cv2.imshow("Segmented Green Areas", segmented_frame)
            cv2.moveWindow("Segmented Green Areas", 1000, 500)  # Move it to (40,30)

        if cv2.waitKey(1) & 0xFF == 27:  # 'Esc' key to stop camera
            stop_camera = True
            break

    if cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()

# Start the camera in a separate thread
camera_thread = threading.Thread(target=run_camera)
camera_thread.start()


# Actual Game Stuff

# Difficulty settings
# Easy      ->  10
# Medium    ->  25
# Hard      ->  40
# Harder    ->  60
# Impossible->  120
difficulty = 10

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

direction = 'RIGHT'
change_to = direction

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
    time.sleep(3)
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

#Function to find the snake's position by searching for green pixels
def find_snake_positions():
    screen_array = pygame.surfarray.array3d(game_window)

    # Find the snake head (custom RGB color: 50, 255, 50)
    head_position = np.argwhere(np.all(screen_array == [50, 255, 50], axis=-1))

    # Find the rest of the snake body (default green: 0, 255, 0)
    body_positions = np.argwhere(np.all(screen_array == [0, 255, 0], axis=-1))

    # Filter positions to only include coordinates that are multiples of 10
    head_position_filtered = [(y, x) for x, y in head_position if x % 10 == 0 and y % 10 == 0]
    body_positions_filtered = [(y, x) for x, y in body_positions if x % 10 == 0 and y % 10 == 0]

    return head_position_filtered, body_positions_filtered

#Function to display the snake's positions on the screen
def show_snake_positions():
    head_position, body_positions = find_snake_positions()

    # Format the positions
    head_str = ', '.join([f'({x}, {y})' for x, y in head_position])
    body_str = ', '.join([f'({x}, {y})' for x, y in body_positions])

    font = pygame.font.SysFont('consolas', 10)

    # Display head position
    head_text = font.render(f'Head Position: {head_str}', True, white)
    game_window.blit(head_text, (10, frame_size_y - 50))

    pygame.draw.rect(game_window, pygame.Color(0, 0, 255), pygame.Rect(snake_body[0][0], snake_body[0][1], 1, 1))

    # Display body positions
    body_text = font.render(f'Body Positions: {body_str}', True, white)
    game_window.blit(body_text, (10, frame_size_y - 30))

# Main logic
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        # Whenever a key is pressed down
        elif event.type == pygame.KEYDOWN:
            # W -> Up; S -> Down; A -> Left; D -> Right
            if event.key == pygame.K_UP or event.key == ord('w'):
                change_to = 'UP'
            if event.key == pygame.K_DOWN or event.key == ord('s'):
                change_to = 'DOWN'
            if event.key == pygame.K_LEFT or event.key == ord('a'):
                change_to = 'LEFT'
            if event.key == pygame.K_RIGHT or event.key == ord('d'):
                change_to = 'RIGHT'
            # Esc -> Create event to quit the game
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))

    # Making sure the snake cannot move in the opposite direction instantaneously
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':
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
        food_spawn = False
    else:
        snake_body.pop()

    # Spawning food on the screen
    if not food_spawn:
        food_pos = [random.randrange(1, (frame_size_x//10)) * 10, random.randrange(1, (frame_size_y//10)) * 10]
    food_spawn = True

    # GFX
    game_window.fill(black)
    # Draw the snake head with a custom color
    pygame.draw.rect(game_window, pygame.Color(50, 255, 50), pygame.Rect(snake_body[0][0], snake_body[0][1], 10, 10))
    # Draw the rest of the snake body with the default green color
    for pos in snake_body[1:]:
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))


    # Snake food
    pygame.draw.rect(game_window, pygame.Color(255, 0, 0), pygame.Rect(food_pos[0], food_pos[1], 10, 10))

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

    show_snake_positions()

    show_score(1, white, 'consolas', 20)
    # Refresh game screen
    pygame.display.update()
    # Refresh rate
    fps_controller.tick(difficulty)

# Wait for the camera thread to finish
camera_thread.join()
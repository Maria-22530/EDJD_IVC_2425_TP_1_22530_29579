# VisualRecognition.py
import threading
import numpy as np
import cv2
import pygame
import os

#Haar Cascade for face detection
classifier_folder = cv2.data.haarcascades
classifier_file = "haarcascade_frontalface_alt.xml"
face_detector = cv2.CascadeClassifier(os.path.join(classifier_folder, classifier_file))


def run_camera(stop_event, change_to):
    cap = cv2.VideoCapture(0)

    while not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            break  #Exit if frame is not captured

        #Flip the image horizontally to coincide with real-life movements
        frame = cv2.flip(frame, 1)  # 1 means horizontal flip

        #Convert to HSV for skin color segmentation
        # hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        # lower_color = np.array([0, 48, 80], dtype=np.uint8)
        # upper_color = np.array([20, 255, 255], dtype=np.uint8)
        # mask = cv2.inRange(hsv_frame, lower_color, upper_color)

        #Detect faces using Haar Cascade
        faces = face_detector.detectMultiScale(frame, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        #Draw rectangles around detected faces
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        #Control logic for face detection
        if len(faces) > 0:
            #Take the largest face (closest to the camera)
            (x, y, w, h) = max(faces, key=lambda rect: rect[2] * rect[3])

            #Divide the frame into directional regions based on the face's position
            height, width = frame.shape[:2]
            if x + w / 2 < width / 3:  #Left third
                change_to[0] = 'LEFT'
            elif x + w / 2 > 2 * width / 3:  #Right third
                change_to[0] = 'RIGHT'
            elif y + h / 2 < height / 3:  #Top third
                change_to[0] = 'UP'
            else:  #Bottom third
                change_to[0] = 'DOWN'

        # #Skin color-based directional controls (fallback if no face detected)
        # if len(faces) == 0:
        #     height, width = frame.shape[:2]
        #     north_region = mask[:height // 2, :]
        #     south_region = mask[height // 2:, :]
        #     west_region = mask[:, :width // 2]
        #     east_region = mask[:, width // 2:]
        #
        #     north_pixels = cv2.countNonZero(north_region)
        #     south_pixels = cv2.countNonZero(south_region)
        #     west_pixels = cv2.countNonZero(west_region)
        #     east_pixels = cv2.countNonZero(east_region)
        #
        #     max_pixels = max(north_pixels, south_pixels, west_pixels, east_pixels)
        #     if max_pixels > 0:
        #         if max_pixels == north_pixels:
        #             change_to[0] = 'UP'
        #         elif max_pixels == south_pixels:
        #             change_to[0] = 'DOWN'
        #         elif max_pixels == west_pixels:
        #             change_to[0] = 'LEFT'
        #         elif max_pixels == east_pixels:
        #             change_to[0] = 'RIGHT'

        #Display the segmented frame with skin color and face detection
        segmented_frame = frame.copy()
        # segmented_frame[mask != 0] = [0, 0, 255]  # Highlight skin pixels in red
        cv2.imshow("Segmented Areas with Faces", segmented_frame)

        #Exit the camera feed on 'Esc'
        if cv2.waitKey(1) & 0xFF == 27:
            stop_event.set()
            pygame.quit()
            break

    if cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()



#Function to find the snake's position
def find_snake_positions(game_window):
    #Capture the current game window screen as a 3D array in RGB format.
    screen_array = pygame.surfarray.array3d(game_window)

    #Convert the RGB screen array to BGR format, as OpenCV expects images in BGR.
    screen_bgr = cv2.cvtColor(screen_array, cv2.COLOR_RGB2BGR)
    #Convert the BGR screen to grayscale, reducing it to one intensity channel for easier processing.
    gray_screen = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)

    #Rotate the grayscale screen 90 degrees counterclockwise and flip it for proper orientation. Might be a simpler way idk
    gray_screen = cv2.rotate(gray_screen, cv2.ROTATE_90_COUNTERCLOCKWISE)
    gray_screen = cv2.flip(gray_screen, 0)

    #cv2.imshow("TestGrays", gray_screen)

    #Apply a binary threshold to the grayscale screen.
    #All pixel values above 240 are set to 255 (white), and others to 0 (black), creating a binary mask.
    _, thresh = cv2.threshold(gray_screen, 230, 255, cv2.THRESH_BINARY)

    #Just a debug thing for the thresholds, warning this makes the game hangup when closing, needs to be force closed if so
    # cv2.imshow("TestThreshold", thresh)

    #Find contours in the thresholded binary image.
    #'contours' holds lists of coordinates representing the boundaries of detected shapes.
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    #These two will be an array of (x, y) coordinates where the head/food is located.
    #Find the position of the snake's head by locating pixels that match their color
    head_position = np.argwhere(np.all(screen_array == [255, 255, 255], axis=-1))
    #Find the position of the food by locating pixels that match their color
    food_position = np.argwhere(np.all(screen_array == [249, 249, 176], axis=-1))

    #Initialize an empty list to store body positions of the snake.
    all_body_pixels = []

    #Loop through each contour found in the binary image.
    for contour in contours:
        #Get the bounding rectangle for the current contour.
        #The rectangle has coordinates (x, y), width, and height.
        x, y, width, height = cv2.boundingRect(contour)

        #Filter small contours to avoid noise (only consider contours larger than 5x5 pixels).
        if width > 5 and height > 5:
            #Append the (x, y) position of the bounding box as a body segment of the snake.
            all_body_pixels.append((x, y))
            #Draw a green rectangle around each contour on the game window for visualization.
            pygame.draw.rect(game_window, pygame.Color(0, 255, 0), pygame.Rect(x, y, width, height), 1)

    return head_position, food_position

#Function to display the snake's positions on the screen
def show_snake_positions(game_window, head_position, food_position):
    font = pygame.font.SysFont('consolas', 10)

    #Render and display each body pixel’s coordinates only if divisible by 10
    for pos in head_position:
        if pos[0] % 10 == 0 and pos[1] % 10 == 0:
            text_surface = font.render(f" {pos[0]},  {pos[1]} ", True, (255, 255, 255))
            game_window.blit(text_surface, pos)

    #Render and display each food pixel’s coordinates only if divisible by 10
    for pos in food_position:
        if pos[0] % 10 == 0 and pos[1] % 10 == 0:
            text_surface = font.render(f" {pos[0]},  {pos[1]} ", True, (255, 255, 255))
            game_window.blit(text_surface, pos)

    pygame.display.flip()
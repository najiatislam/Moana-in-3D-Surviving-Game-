from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time
from math import sin, cos, radians

# Game constants
ISLAND_SIZE = 800
MAX_ARROWS = 30
RELOAD_TIME = 10  # seconds
GAME_DURATION = 180  # 3 minutes in seconds
ANIMAL_SPAWN_RATE = 5 # seconds
TREASURE_SPAWN_RATE = 15  # seconds
WAVE_ANIMATION_SPEED = 0.02
OCEAN_BOUNDARY_RADIUS = ISLAND_SIZE * 0.9 + 50  # Add a buffer to allow Moana to fetch water
MAX_WATER_BOTTLES = 5

BOAT_SPAWN_SCORE = 50  # Score needed for boat to appear

# Game state
moana_pos = [0, 0, 20]  # Moana's position
arrows_angle = 0
moana_life = 5
arrows_left = MAX_ARROWS
arrows_missed = 0
game_over = False
game_won = False
reloading = False
reload_start_time = 0
game_start_time = 0
fetch_message_start_time = 0
score = 0
wave_offset = 0
water_bottles = 0  # Initialize water bottles
boat_spawned = False
boat_pos = [0, 0, 0]
boat_escape = False

# Camera state
camera_pos = [0, 500, 500]
camera_angle = 0
first_person_mode = False


def draw_moana():
    glPushMatrix()
    glTranslatef(moana_pos[0], moana_pos[1], moana_pos[2])

    if game_over:
        glRotatef(90, 1, 0, 0)
    else:
        glRotatef(arrows_angle, 0, 0, 1)

    # Moana's body (brown dress)
    glColor3f(0.5, 0.3, 0.1)
    glPushMatrix()
    glTranslatef(0, 0, 25)
    glScalef(15, 10, 30)
    glutSolidCube(1)
    glPopMatrix()

    # Moana's head
    glColor3f(0.9, 0.7, 0.5)  # Skin tone
    glPushMatrix()
    glTranslatef(0, 0, 50)
    quadric = gluNewQuadric()  # Create a new quadric object
    gluSphere(quadric, 8, 20, 20) 
    glPopMatrix()

    # Hair (long, wavy)
    glColor3f(0.2, 0.1, 0.05)  # Dark brown
    glPushMatrix()
    glTranslatef(0, 0, 45)
    glRotatef(90, 1, 0, 0)
    gluCylinder(gluNewQuadric(), 8, 5, 20, 20, 1)
    glPopMatrix()

    # Arrows (quiver)
    if not first_person_mode:
        glColor3f(0.6, 0.5, 0.3)  # Bamboo color
        glPushMatrix()
        glTranslatef(10, 0, 40)
        glRotatef(90, 0, 1, 0)
        gluCylinder(gluNewQuadric(), 5, 5, 20, 10, 1)
        glPopMatrix()

    # Bow (wooden)
    glColor3f(0.4, 0.3, 0.1)  # Wood color
    glPushMatrix()
    glTranslatef(0, 0, 40)
    if not game_over:
        glRotatef(45, 0, 1, 0)  # Bow angle
    glutSolidTorus(2, 15, 10, 10)
    glPopMatrix()

    glPopMatrix()


def draw_treasures():
    global treasures
    
    # Ensure there is at least one treasure
    if len(treasures) == 0:
        treasures.append(spawn_treasure())
    
    # Draw all treasures
    for treasure in treasures:
        glPushMatrix()
        glTranslatef(treasure['pos'][0], treasure['pos'][1], treasure['pos'][2])
        
        # Draw the golden square (base of the treasure)
        glColor3f(0.8, 0.6, 0.2)  # Gold color
        glPushMatrix()
        glScalef(30, 20, 10)  # Scale the square
        glutSolidCube(1)
        glPopMatrix()

        # Draw the sphere (circle) on top of the square
        glColor3f(1.0, 0.0, 0.0)  # Red
        glPushMatrix()
        glTranslatef(0, 0, 10)  # Position the sphere on top of the scaled cube
        quadric = gluNewQuadric()  # Create a new quadric object
        gluSphere(quadric, 3, 20, 20) 
        glPopMatrix()

        glPopMatrix()


# =============== CAMERA FUNCTIONS ===============
def setupCamera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.25, 0.1, 1500)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if first_person_mode:
        # First-person view from Moana's perspective
        angle_rad = radians(arrows_angle)
        eye_x = moana_pos[0] + math.cos(angle_rad) * 10
        eye_y = moana_pos[1] + math.sin(angle_rad) * 10
        eye_z = moana_pos[2] + 20  # Eye level
        
        center_x = moana_pos[0] + math.cos(angle_rad) * 100
        center_y = moana_pos[1] + math.sin(angle_rad) * 100
        center_z = moana_pos[2] + 10
        
        gluLookAt(eye_x, eye_y, eye_z,
                 center_x, center_y, center_z,
                 0, 0, 1)
    else:
        # Third-person view orbiting Moana
        cam_x = moana_pos[0] + 300 * math.sin(radians(camera_angle))
        cam_y = moana_pos[1] + 300 * math.cos(radians(camera_angle))
        cam_z = camera_pos[2]
        
        gluLookAt(cam_x, cam_y, cam_z,
                 moana_pos[0], moana_pos[1], moana_pos[2],
                 0, 0, 1)


def start_reload():
    global reloading, reload_start_time
    reloading = True
    reload_start_time = time.time()

def check_reload():
    global reloading, arrows_left
    if reloading and time.time() - reload_start_time >= RELOAD_TIME:
        reloading = False
        arrows_left = MAX_ARROWS



def check_game_time():
    global game_won
    current_time = time.time()
    if current_time - game_start_time >= GAME_DURATION and not game_over:
        game_won = True

  
    current_time = time.time()
    time_left = max(0, GAME_DURATION - (current_time - game_start_time))
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    draw_text(10, 590, f"Time Left: {minutes:02d}:{seconds:02d}")


# =============== GAME LOGIC FUNCTIONS ===============

def check_boat_spawn():
    global boat_spawned, boat_pos, fetch_message, fetch_message_start_time
    
    if not boat_spawned and score >= BOAT_SPAWN_SCORE:
        # Place boat at random position in the ocean
        angle = random.uniform(0, 2 * math.pi)
        radius = ISLAND_SIZE * 0.85  # Just beyond the island's edge
        
        boat_pos = [
            radius * math.cos(angle),
            radius * math.sin(angle),
            0  # At water level
        ]
        
        boat_spawned = True
        fetch_message = "A boat has appeared in the ocean!"
        fetch_message_start_time = time.time()
        print("A boat has appeared in the ocean!")


def check_boat_escape():
    global game_won, boat_escape
    
    if not boat_spawned or boat_escape:
        return
        
    # Check if Moana is near the boat
    dx = moana_pos[0] - boat_pos[0]
    dy = moana_pos[1] - boat_pos[1]
    distance = math.sqrt(dx*dx + dy*dy)
    
    if distance < 50:  # Close enough to board
        boat_escape = True
        game_won = True
        print("Moana escaped from the island and wins!")



def draw_boat():
    if not boat_spawned:
        return  # Do not draw the boat if it hasn't spawned

    glPushMatrix()
    glTranslatef(boat_pos[0], boat_pos[1], boat_pos[2])  # Position the boat at `boat_pos`

    # Scale the entire boat to make it larger
    glScalef(2.0, 2.0, 2.0)  # Increase the scaling factors (x, y, z)

    # Draw the boat base
    glColor3f(0.5, 0.3, 0.1)  # Brown color for the boat
    glPushMatrix()
    glScalef(30, 10, 5)  # Scale the boat base
    glutSolidCube(1)
    glPopMatrix()

    # Draw the mast
    glColor3f(0.8, 0.8, 0.8)  # Gray color for the mast
    glPushMatrix()
    glTranslatef(0, 0, 10)  # Position the mast above the boat base
    glRotatef(-90, 1, 0, 0)  # Rotate to make the mast vertical
    gluCylinder(gluNewQuadric(), 0.5, 0.5, 20, 10, 10)  # Mast
    glPopMatrix()

    # Draw the sail
    glColor3f(1.0, 1.0, 1.0)  # White color for the sail
    glPushMatrix()
    glTranslatef(0, 0, 15)  # Position the sail above the boat base
    glRotatef(90, 0, 1, 0)  # Rotate to align the sail
    glScalef(15, 20, 1)  # Scale the sail
    glutSolidCube(1)
    glPopMatrix()

    glPopMatrix()




def keyboardListener(key, x, y):
    global moana_pos, arrows_angle, game_over, game_won, moana_life, fetch_message, fetch_message_start_time
    
    if game_over or game_won:
        if key == b'r':
            init_game()
        return
    
    key = key.decode('utf-8').lower() if hasattr(key, 'decode') else key
    move_speed = 10
    rotate_speed = 5
    
    if key == 'w':
        moana_pos[0] += math.cos(radians(arrows_angle)) * move_speed
        moana_pos[1] += math.sin(radians(arrows_angle)) * move_speed
    elif key == 's':
        moana_pos[0] -= math.cos(radians(arrows_angle)) * move_speed
        moana_pos[1] -= math.sin(radians(arrows_angle)) * move_speed
    elif key == 'd':
        moana_pos[0] += math.cos(radians(arrows_angle - 90)) * move_speed
        moana_pos[1] += math.sin(radians(arrows_angle - 90)) * move_speed
    elif key == 'a':
        moana_pos[0] += math.cos(radians(arrows_angle + 90)) * move_speed
        moana_pos[1] += math.sin(radians(arrows_angle + 90)) * move_speed
    elif key == 'z':
        arrows_angle = (arrows_angle + rotate_speed) % 360
    elif key == 'x':
        arrows_angle = (arrows_angle - rotate_speed) % 360
    elif key == 'o' and not reloading:
        start_reload()
    
    elif key == 'v':  # Fetch water from the ocean
        print("V key pressed!")  # Debugging output
        fetch_message = fetch_water()
    
    elif key == ' ':  # Space key to board boat
        if boat_spawned:
            check_boat_escape()
    
    # Keep Moana within the ocean boundary
    distance_from_center = math.sqrt(moana_pos[0]**2 + moana_pos[1]**2)
    if distance_from_center > OCEAN_BOUNDARY_RADIUS:
        # Clamp Moana's position to the ocean boundary
        angle = math.atan2(moana_pos[1], moana_pos[0])
        moana_pos[0] = math.cos(angle) * OCEAN_BOUNDARY_RADIUS
        moana_pos[1] = math.sin(angle) * OCEAN_BOUNDARY_RADIUS

def main():
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    glutCreateWindow(b"Moana in Survival Island")
    
    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    
    # Initialize game state
    init_game()
    
    # Register callback functions
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    # Start the main loop
    glutMainLoop()

if __name__ == "__main__":
    main()
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
RELOAD_TIME = 10 

# Camera state
camera_pos = [0, 500, 500]
camera_angle = 0
first_person_mode = False

fetch_message = ""

# Game state
moana_pos = [0, 0, 20] 
moana_life = 5
game_over = False
game_won = False
arrows_angle = 0
arrows_left = MAX_ARROWS
reloading = False
reload_start_time = 0
fetch_message_start_time = 0
water_bottles = 0  # Initialize water bottles



# =============== INITIALIZATION FUNCTIONS ===============
def init_game():
    global moana_pos, arrows_angle, moana_life, arrows_left, arrows_missed
    global game_over, game_won, reloading, reload_start_time, game_start_time, score
    global arrows, animals, treasures, palm_trees, wave_offset, trap_zones, water_bottles
    global boat_spawned, boat_pos, boat_escape

    moana_pos = [0, 0, 20]
    arrows_angle = 0
    moana_life = 5
    arrows_left = MAX_ARROWS
    arrows_missed = 0
    game_over = False
    game_won = False
    reloading = False
    reload_start_time = 0
    game_start_time = time.time()
    score = 0
    wave_offset = 0
    water_bottles = 0
    boat_spawned = False
    boat_pos = [0, 0, 0]
    boat_escape = False

    arrows = []
    animals = []
    treasures = []
    palm_trees = []
    trap_zones = []
    
    # Spawn initial animals
    for _ in range(5):
        spawn_animal()
    

    

    # Generate trap zones
    
    for _ in range(5):  # Create 5 trap zones
        while True:
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(0, ISLAND_SIZE * 0.7)  # Trap zones are within the island
            x = math.cos(angle) * distance
            y = math.sin(angle) * distance
            
            # Ensure trap zone doesn't spawn too close to Moana
            dx = x - moana_pos[0]
            dy = y - moana_pos[1]
            dist = math.sqrt(dx * dx + dy * dy)
            
            if dist > 100:  # Minimum distance from Moana
                trap_zones.append({
                    'pos': [x, y],
                    'radius': random.uniform(5, 20)  # Random radius for trap zones
                })
                break
    
    # Spawn the first treasure
    treasures.append(spawn_treasure())


# =============== GAME LOGIC FUNCTIONS ===============

def fetch_water():
    global water_bottles, fetch_message, fetch_message_start_time
    
    # Check if Moana is near the ocean boundary
    distance_from_center = math.sqrt(moana_pos[0]**2 + moana_pos[1]**2)
    if distance_from_center >= ISLAND_SIZE * 0.9:  # Near the ocean
        water_bottles += 1
        fetch_message = "Water fetched successfully!"
        fetch_message_start_time = time.time()
        print(f"Water fetched! Total water bottles: {water_bottles}")
    else:
        fetch_message = "Move closer to the ocean to fetch water."
        fetch_message_start_time = time.time()
        print("Too far from the ocean to fetch water.")

def check_collisions():
    global moana_life, game_over
    
    # Check collisions with animals
    for animal in animals:
        dx = moana_pos[0] - animal['pos'][0]
        dy = moana_pos[1] - animal['pos'][1]
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist < 30:  # Collision radius
            moana_life -= 1
            print(f"Collision with animal! Moana's life: {moana_life}")
            if moana_life <= 0:
                game_over = True
                print("Game Over!")
            return  # Only one collision per frame
    
    # Check collisions with traps
    for trap in trap_zones:
        dx = moana_pos[0] - trap['pos'][0]
        dy = moana_pos[1] - trap['pos'][1]
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist < trap['radius']:  # Collision with trap
            moana_life -= 1
            print(f"Collision with trap! Moana's life: {moana_life}")
            if moana_life <= 0:
                game_over = True
                print("Game Over!")
            return  # Only one collision per frame



def spawn_treasure():
    while True:
        x = random.uniform(-ISLAND_SIZE // 2, ISLAND_SIZE // 2)
        y = random.uniform(-ISLAND_SIZE // 2, ISLAND_SIZE // 2)
        
        # Ensure treasure doesn't spawn too close to Moana
        dx = x - moana_pos[0]
        dy = y - moana_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 100 and math.sqrt(x**2 + y**2) <= ISLAND_SIZE * 0.9:
            return {
                'pos': [x, y, 5]  # Z-position is fixed above the ground
            }

def update_arrows():
    global arrows, arrows_missed, moana_life, game_over
    
    for arrow in arrows[:]:
        # Update arrow position
        angle_rad = radians(arrow['angle'])
        arrow['pos'][0] += math.cos(angle_rad) * 20  # Move forward
        arrow['pos'][1] += math.sin(angle_rad) * 20  # Move forward
        
        # Check if the arrow is out of bounds
        if abs(arrow['pos'][0]) > ISLAND_SIZE or abs(arrow['pos'][1]) > ISLAND_SIZE:
            arrows.remove(arrow)  # Remove the missed arrow
            arrows_missed += 1
            print(f"Arrow missed! Total missed: {arrows_missed}")
            
            # Deduct 1 life after 10 missed arrows
            if arrows_missed >= 10:
                arrows_missed = 0  # Reset missed counter
                moana_life -= 1
                print(f"10 missed arrows! Moana's life: {moana_life}")
                
                if moana_life <= 0:
                    game_over = True
                    print("Game Over!")

def update_treasures():
    global treasures, moana_life
    
    if len(treasures) == 0:
        return  # No treasure to update
    
    treasure = treasures[0]  # Only one treasure at a time
    dx = moana_pos[0] - treasure['pos'][0]
    dy = moana_pos[1] - treasure['pos'][1]
    dist = math.sqrt(dx * dx + dy * dy)
    
    # Check if Moana collides with the treasure
    if dist < 25:  # Collision radius
        moana_life = min(5, moana_life + 1)  # Restore Moana's life
        print(f"Treasure collected! Moana's life increased to {moana_life}.")
        
        # Remove the collected treasure
        treasures.pop(0)
        
        # Spawn a new treasure
        treasures.append(spawn_treasure())
def fire_arrow():
    global arrows_left
    
    if game_over or game_won or reloading or arrows_left <= 0:
        return
    
    angle_rad = radians(arrows_angle)
    arrow_length = 25  # Distance from Moana's position to the arrow's starting point
    
    # Arrow starting position
    start_x = moana_pos[0] + math.cos(angle_rad) * arrow_length
    start_y = moana_pos[1] + math.sin(angle_rad) * arrow_length
    start_z = moana_pos[2] + 40  # Bow height
    
    arrows.append({
        'pos': [start_x, start_y, start_z],
        'angle': arrows_angle
    })
    
    arrows_left -= 1
    
    if arrows_left == 0:
        start_reload()

def start_reload():
    global reloading, reload_start_time
    reloading = True
    reload_start_time = time.time()


def check_reload():
    global reloading, arrows_left
    if reloading and time.time() - reload_start_time >= RELOAD_TIME:
        reloading = False
        arrows_left = MAX_ARROWS 

# =============== INPUT HANDLERS ===============


def mouseListener(button, state, x, y):
    global first_person_mode
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_mode = not first_person_mode



def specialKeyListener(key, x, y):
    global camera_angle, camera_pos
    
    if key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle + 5) % 360  # Rotate camera clockwise
    elif key == GLUT_KEY_LEFT:
        camera_angle = (camera_angle - 5) % 360  # Rotate camera counterclockwise
    elif key == GLUT_KEY_UP:
        camera_pos[2] = min(1000, camera_pos[2] + 20)  # Zoom out
    elif key == GLUT_KEY_DOWN:
        camera_pos[2] = max(100, camera_pos[2] - 20)  # Zoom in


def keyboardListener(key, x, y):
    global moana_pos, arrows_angle, game_over, game_won, moana_life, fetch_message, fetch_message_start_time
    
    if game_over or game_won:
        if key == b'r':
            init_game()
        return
    
    key = key.decode('utf-8').lower() if hasattr(key, 'decode') else key
    
    if key == 'o' and not reloading:
        start_reload()
    elif key == 'v':  # Fetch water
        fetch_water()


# =============== DRAWING FUNCTIONS ===============


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
        gluSphere(quadric, 3, 20, 20)  # Sphere with radius 3
        glPopMatrix()

        glPopMatrix()


def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)




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





# =============== MAIN GAME FUNCTIONS ===============

def idle():
    if not game_over and not game_won:

        check_reload()
        update_treasures()
        check_collisions()
        update_arrows()


    
    glutPostRedisplay()




def showScreen():
    global moana_life, fetch_message, fetch_message_start_time, water_bottles
    
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Set up camera
    setupCamera()
    
    # Draw game elements
    
    draw_treasures()
    
    
    # Display Moana's life and missed arrows
    glColor3f(1.0, 1.0, 0.8)  # Light yellow text
    draw_text(10, 770, f"Moana's Life: {moana_life}")
    draw_text(10, 740, f"Missed Arrows: {arrows_missed}")
    
    glutSwapBuffers()






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


fetch_message = ""
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
    
    # Create palm trees around the island
    for i in range(12):  # 12 trees around the perimeter
        angle = i * (360/12)
        distance = ISLAND_SIZE * 0.8  # Place near the edge
        x = math.cos(radians(angle)) * distance
        y = math.sin(radians(angle)) * distance
        palm_trees.append({
            'pos': [x, y, 0],
            'size': random.uniform(0.8, 1.2)  # Vary tree sizes
        })
    
    # Add some random trees inside the island
    for i in range(8):  # 8 more trees scattered around
        angle = random.uniform(0, 360)
        distance = random.uniform(ISLAND_SIZE * 0.3, ISLAND_SIZE * 0.7)
        x = math.cos(radians(angle)) * distance
        y = math.sin(radians(angle)) * distance
        palm_trees.append({
            'pos': [x, y, 0],
            'size': random.uniform(0.6, 1.0)  # Slightly smaller trees
        })
    
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





def spawn_animal():
    while True:
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(100, ISLAND_SIZE * 0.9)  # Ensure animals spawn at least 100 units away
        x = moana_pos[0] + math.cos(angle) * distance
        y = moana_pos[1] + math.sin(angle) * distance
        
        # Ensure the animal spawns within the island's radius
        if math.sqrt(x**2 + y**2) <= ISLAND_SIZE * 0.9:
            # Check if the animal is far enough from Moana
            dx = x - moana_pos[0]
            dy = y - moana_pos[1]
            dist = math.sqrt(dx * dx + dy * dy)
            if dist >= 100:  # Minimum distance from Moana
                animal_type = random.choice(['deer', 'rabbit', 'wild_boar'])  # Randomly assign type
                return {
                    'pos': [x, y, 10],  # Z-position is fixed above the ground
                    'speed': random.uniform(0.1, 0.3),
                    'type': animal_type
                }


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
        


def fetch_water():
    global fetch_message, fetch_message_start_time, water_bottles
    distance_from_center = math.sqrt(moana_pos[0]**2 + moana_pos[1]**2)
    
    # Check if Moana is near the ocean boundary
    if ISLAND_SIZE * 0.9 < distance_from_center <= OCEAN_BOUNDARY_RADIUS:
        # Check if bottles are full
        if water_bottles < MAX_WATER_BOTTLES:
            # Increase water bottles count
            water_bottles += 1
            print(f"Moana fetched water! Bottles: {water_bottles}")

            # Set the fetch message and start time
            fetch_message = "Moana fetched water!"
            fetch_message_start_time = time.time()
        else:
            # Bottles are full
            fetch_message = "Bottles are full!"
            fetch_message_start_time = time.time()
            print("Bottles are full! Cannot fetch more water.")
    else:
        print("Moana is too far from the ocean to fetch water.")
        fetch_message = "Too far from ocean!"
        fetch_message_start_time = time.time()


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


def fire_arrow():
    global arrows_left
    
    if game_over or game_won or reloading or arrows_left <= 0:
        return
    
    angle_rad = radians(arrows_angle)
    arrow_length = 25   # Distance from Moana's position to the arrow's starting point
    
    # Arrow starting position
    start_x = moana_pos[0] + math.cos(angle_rad) * arrow_length
    start_y = moana_pos[1] + math.sin(angle_rad) * arrow_length
    start_z = moana_pos[2] + 40  # Bow height
    
    arrows.append({
        'pos': [start_x, start_y, start_z],
        'angle': arrows_angle
    })
    
    arrows_left -= 1
    
    # Print stats when arrow is fired
    # print(f"Arrow Fired! Arrows left: {arrows_left}")
    
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



def update_arrows():
    global arrows, arrows_missed, score, moana_life, animals
    
    arrows_to_remove = set()
    animals_to_remove = set()
    
    for i, arrow in enumerate(arrows):
        # Move arrow
        angle_rad = radians(arrow['angle'])
        arrow['pos'][0] += cos(angle_rad) * 15
        arrow['pos'][1] += sin(angle_rad) * 15
        arrow['pos'][2] -= 0.5  # Gravity effect
        
        # Check if arrow is out of bounds
        if (abs(arrow['pos'][0]) > ISLAND_SIZE or 
            abs(arrow['pos'][1]) > ISLAND_SIZE or 
            arrow['pos'][2] <= 0):
            arrows_to_remove.add(i)
            arrows_missed += 1
            if arrows_missed % 10 == 0:
                moana_life -= 1
            continue
        
        # Check for animal hits
        for j, animal in enumerate(animals):
            dx = arrow['pos'][0] - animal['pos'][0]
            dy = arrow['pos'][1] - animal['pos'][1]
            dz = arrow['pos'][2] - animal['pos'][2]
            distance = math.sqrt(dx * dx + dy * dy + dz * dz)
            
            if distance < 50:  # Hit radius
                arrows_to_remove.add(i)
                animals_to_remove.add(j)
                score += 10
                print(f"Animal hit! Score: {score}")
                
                # Check if boat should spawn after score update
                if score >= BOAT_SPAWN_SCORE and not boat_spawned:
                    check_boat_spawn()
                break
    
    # Remove arrows and animals
    for i in sorted(arrows_to_remove, reverse=True):
        if i < len(arrows):
            arrows.pop(i)
    
    for j in sorted(animals_to_remove, reverse=True):
        if j < len(animals):
            animals.pop(j)
            animals.append(spawn_animal())




def update_animals():
    global moana_life, game_over
    
    if game_over or game_won:
        return
    
    # Spawn new animals periodically
    current_time = time.time()
    if current_time - game_start_time > ANIMAL_SPAWN_RATE and len(animals) < 6:
        animals.append(spawn_animal())
    
    # Move animals towards player
    for animal in animals:
        dx = moana_pos[0] - animal['pos'][0]
        dy = moana_pos[1] - animal['pos'][1]
        dist = math.sqrt(dx * dx + dy * dy)
        
        if dist > 0:
            animal['pos'][0] += (dx / dist) * animal['speed']
            animal['pos'][1] += (dy / dist) * animal['speed']
        
        # Check for player collision
        if dist < 25:
            moana_life -= 1
            print(f"Collision detected! Moana's life reduced to {moana_life}.")
            animal['pos'][0] -= (dx / dist) * 50
            animal['pos'][1] -= (dy / dist) * 50
            
            if moana_life <= 0:
                game_over = True
                print("Game Over! Moana's life has reached zero.")


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


def check_game_time():
    global game_won
    current_time = time.time()
    if current_time - game_start_time >= GAME_DURATION and not game_over:
        game_won = True

# =============== DRAWING FUNCTIONS ===============
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


def draw_trap_zones():
    glColor3f(0, 0, 0)  # black trap zone color
    for trap in trap_zones:
        glPushMatrix()
        glTranslatef(trap['pos'][0], trap['pos'][1], 0)
        glBegin(GL_TRIANGLE_FAN)
        glVertex3f(0, 0, 0)  # Center of the trap zone
        for i in range(361):  # Draw a circle
            angle = radians(i)
            x = math.cos(angle) * trap['radius']
            y = math.sin(angle) * trap['radius']
            glVertex3f(x, y, 0)
        glEnd()
        glPopMatrix()



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


def draw_arrows():
    for arrow in arrows:
        glPushMatrix()
        glTranslatef(arrow['pos'][0], arrow['pos'][1], arrow['pos'][2])
        
        # Rotate the arrow to point in the correct direction
        glRotatef(arrow['angle'], 0, 0, 1)  # Add 180 degrees to flip the arrowhead
        
        # Arrow shaft
        glColor3f(0.6, 0.3, 0.1)  # Brown shaft
        glPushMatrix()
        glRotatef(90, 0, 1, 0)  # Rotate to align with the X-axis
        gluCylinder(gluNewQuadric(), 0.5, 0.5, 20, 10, 1)
        glPopMatrix()
        
        # Arrowhead (stone tip)
        glColor3f(0.5, 0.5, 0.5)  # Gray arrowhead
        glPushMatrix()
        glTranslatef(20, 0, 0)  # Position the arrowhead at the tip of the shaft
        glutSolidCone(2, 5, 10, 10)
        
        glPopMatrix()
        
        glPopMatrix()





def draw_animals():

    for animal in animals:
        glPushMatrix()
        glTranslatef(animal['pos'][0], animal['pos'][1], animal['pos'][2])
        
        # Check the type of animal and draw accordingly
        if animal.get('type') == 'deer':
            draw_deer()
        elif animal.get('type') == 'rabbit':
            draw_rabbit()
        elif animal.get('type') == 'wild_boar':
            draw_wild_boar()
        else:
            # Default: Wild boar if no type is specified
            draw_wild_boar()
        
        glPopMatrix()


def draw_deer():
    # Body
    glColor3f(0.6, 0.4, 0.2)  # Brown
    glPushMatrix()
    glScalef(1.2, 0.6, 0.6)  # Scale the body (smaller)
    glutSolidCube(20)  # Smaller cube
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(15, 0, 10)  # Position the head
    glColor3f(0.6, 0.4, 0.2)  # Brown
    glutSolidCube(10)  # Smaller head
    glPopMatrix()
    
    # Legs
    glColor3f(0.4, 0.2, 0.1)  # Darker brown
    for x, y in [(-10, -8), (10, -8), (-10, 8), (10, 8)]:
        glPushMatrix()
        glTranslatef(x, y, -10)  # Position the legs
        gluCylinder(gluNewQuadric(), 2, 2, 15, 10, 10)  # Thinner, shorter legs
        glPopMatrix()
    
    # Antlers
    glColor3f(0.4, 0.2, 0.1)  # Dark brown
    for x in [12, 18]:
        glPushMatrix()
        glTranslatef(x, 0, 20)  # Position the antlers
        glRotatef(45, 0, 1, 0)  # Rotate slightly
        gluCylinder(gluNewQuadric(), 0.5, 0.5, 10, 10, 10)  # Smaller antlers
        glPopMatrix()



def draw_rabbit():
    # Body
    glColor3f(0.9, 0.9, 0.9)  # Light gray
    glPushMatrix()
    glScalef(1.0, 0.6, 0.6)  # Scale the body (smaller)
    glutSolidCube(15)  # Smaller cube
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(12, 0, 8)  # Position the head
    glColor3f(0.9, 0.9, 0.9)  # Light gray
    quadric = gluNewQuadric()  # Create a new quadric object
    gluSphere(quadric, 8, 20, 20) 
    glPopMatrix()
    
    # Ears
    glColor3f(0.9, 0.9, 0.9)  # Light gray
    for x in [10, 14]:
        glPushMatrix()
        glTranslatef(x, 0, 18)  # Position the ears
        glRotatef(90, 1, 0, 0)  # Rotate vertically
        gluCylinder(gluNewQuadric(), 1, 1, 10, 10, 10)  # Smaller ears
        glPopMatrix()
    
    # Legs
    glColor3f(0.8, 0.8, 0.8)  # Slightly darker gray
    for x, y in [(-8, -5), (8, -5), (-8, 5), (8, 5)]:
        glPushMatrix()
        glTranslatef(x, y, -8)  # Position the legs
        gluCylinder(gluNewQuadric(), 1, 1, 10, 10, 10)  # Smaller legs
        glPopMatrix()


def draw_wild_boar():
    # Body
    glColor3f(0.4, 0.2, 0.1)  # Dark brown
    glPushMatrix()
    glScalef(1.5, 0.8, 0.8)  # Scale the body (smaller)
    glutSolidCube(25)  # Smaller cube
    glPopMatrix()
    
    # Head
    glPushMatrix()
    glTranslatef(20, 0, 10)  # Position the head
    glColor3f(0.4, 0.2, 0.1)  # Dark brown
    quadric = gluNewQuadric()  # Create a new quadric object
    gluSphere(quadric, 10, 20, 20)  
    glPopMatrix()
    
    # Legs
    glColor3f(0.3, 0.15, 0.1)  # Darker brown
    for x, y in [(-15, -8), (15, -8), (-15, 8), (15, 8)]:
        glPushMatrix()
        glTranslatef(x, y, -12)  # Position the legs
        gluCylinder(gluNewQuadric(), 2, 2, 15, 10, 10)  # Thinner, shorter legs
        glPopMatrix()
    
    # Tusks
    glColor3f(1, 1, 1)  # White
    for x in [18, 22]:
        glPushMatrix()
        glTranslatef(x, 2, 12)  # Position the tusks
        glRotatef(45, 0, 1, 0)  # Rotate slightly
        gluCylinder(gluNewQuadric(), 0.5, 0.5, 5, 10, 10)  # Smaller tusks
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


def draw_palm_trees():
    for tree in palm_trees:
        glPushMatrix()
        glTranslatef(tree['pos'][0], tree['pos'][1], 0)  # Ensure trees are on the ground
        scale = tree['size']
        glScalef(scale, scale, scale)
        
        # Trunk
        glColor3f(0.5, 0.3, 0.1)  # Brown trunk
        glPushMatrix()
        glRotatef(-90, 1, 0, 0)  # Rotate to make trunk vertical
        gluCylinder(gluNewQuadric(), 5, 3, 50, 10, 10)  # Tapered trunk
        glPopMatrix()
        
        # Coconuts
        glColor3f(0.4, 0.3, 0.1)  # Coconut color
        for i in range(3):
            angle = i * 120
            radius = 8
            x = cos(radians(angle)) * radius
            y = sin(radians(angle)) * radius
            glPushMatrix()
            glTranslatef(x, y, 50)  # Position coconuts at the top of the trunk
            gluSphere(gluNewQuadric(), 4, 10, 10)  # Coconut
            glPopMatrix()
        
        # Leaves
        glColor3f(0.1, 0.5, 0.1)  # Green leaves
        for i in range(6):
            angle = i * 60
            glPushMatrix()
            glTranslatef(0, 0, 50)  # Start leaves at the top of the trunk
            glRotatef(angle, 0, 0, 1)  # Spread leaves in a circle
            glRotatef(45, 1, 0, 0)  # Angle leaves downward
            gluCylinder(gluNewQuadric(), 0, 15, 40, 10, 10)  # Leaf frond
            glPopMatrix()
        
        glPopMatrix()



def draw_island():
    global wave_offset


    glPushMatrix()
    glColor3f(0.9, 0.8, 0.5)  # Sand color
    glBegin(GL_TRIANGLES)
    for i in range(360):  # 360 degrees
        angle1 = radians(i)
        angle2 = radians(i + 1)
        radius = ISLAND_SIZE * 0.9

        # Center of the island
        glVertex3f(0, 0, 0)

        # First vertex on the circle
        x1 = math.cos(angle1) * radius
        y1 = math.sin(angle1) * radius
        glVertex3f(x1, y1, 0)

        # Second vertex on the circle
        x2 = math.cos(angle2) * radius
        y2 = math.sin(angle2) * radius
        glVertex3f(x2, y2, 0)
    glEnd()
    glPopMatrix()
    

    
    # Draw ocean with waves
    wave_offset += WAVE_ANIMATION_SPEED
    glPushMatrix()
    glBegin(GL_QUADS)
    glColor3f(0.1, 0.3, 0.6)  # Ocean color
    
    # Create wave pattern
    for i in range(-ISLAND_SIZE, ISLAND_SIZE, 50):
        for j in range(-ISLAND_SIZE, ISLAND_SIZE, 50):
            wave_height = 2 * math.sin((i + wave_offset * 100) * 0.05) * math.cos((j + wave_offset * 100) * 0.05)
            
            glVertex3f(i, j, -5 + wave_height)
            glVertex3f(i + 50, j, -5 + wave_height)
            glVertex3f(i + 50, j + 50, -5 + wave_height)
            glVertex3f(i, j + 50, -5 + wave_height)
    glEnd()
    glPopMatrix()


def draw_ocean_boundary():
    glColor3f(0.0, 0.0, 1.0)  # Blue color for the boundary
    glBegin(GL_LINE_LOOP)
    for i in range(360):
        angle = radians(i)
        x = math.cos(angle) * OCEAN_BOUNDARY_RADIUS
        y = math.sin(angle) * OCEAN_BOUNDARY_RADIUS
        glVertex3f(x, y, 0)
    glEnd()




def draw_sky():
    # Save the current matrix state
    glPushMatrix()
    
    # Save projection matrix
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    # Switch to modelview for drawing
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    # Draw tropical sky gradient
    glBegin(GL_QUADS)
    # Top color (light blue)
    glColor3f(0.6, 0.8, 1.0)
    glVertex2f(0, 800)
    glVertex2f(1000, 800)
    
    # Horizon color (orange)
    glColor3f(1.0, 0.7, 0.4)
    glVertex2f(1000, 400)
    glVertex2f(0, 400)
    
    # Ocean color (blue)
    glColor3f(0.1, 0.3, 0.6)
    glVertex2f(1000, 0)
    glVertex2f(0, 0)
    glEnd()
    
    # Restore matrices
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)
    
    # Clear the depth buffer to ensure the sky does not interfere with other objects
    glClear(GL_DEPTH_BUFFER_BIT)
    
    # Restore the original matrix state
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

# =============== INPUT HANDLERS ===============


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

    # Check for collision with trap zones
    for trap in trap_zones:
        dx = moana_pos[0] - trap['pos'][0]
        dy = moana_pos[1] - trap['pos'][1]
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < trap['radius']:
            moana_life -= 1
            if moana_life < 0:
                moana_life = 0  # Prevent negative life
            print(f"Moana stepped into a trap! Life reduced to {moana_life}.")
            if moana_life <= 0:
                game_over = True
                print("Game Over! Moana's life has reached zero.")



def specialKeyListener(key, x, y):
    global camera_angle, camera_pos
    
    if key == GLUT_KEY_RIGHT:
        camera_angle = (camera_angle + 5) % 360
    elif key == GLUT_KEY_LEFT :
        camera_angle = (camera_angle - 5) % 360
    elif key == GLUT_KEY_UP:
        camera_pos[2] = min(1000, camera_pos[2] + 20)
    elif key == GLUT_KEY_DOWN:
        camera_pos[2] = max(100, camera_pos[2] - 20)

def mouseListener(button, state, x, y):
    global first_person_mode
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN and not (game_over or game_won):
        fire_arrow()
    elif button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_mode = not first_person_mode

# =============== MAIN GAME FUNCTIONS ===============
def idle():
    if not game_over and not game_won:
        update_arrows()
        update_animals()
        update_treasures()
        check_game_time()
        check_reload()
        check_boat_spawn()


    glutPostRedisplay()

def showScreen():

    global fetch_message, fetch_message_start_time  # Declare global variables
    # Clear buffers
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Draw sky (before camera setup)
    draw_sky()
    
    # Set up camera
    setupCamera()
    
    # Draw island environment
    draw_island()
    draw_ocean_boundary()  # Draw the ocean boundary
    draw_trap_zones()  # Draw trap zones
    draw_palm_trees()  # Draw the palm trees
    
    # Draw game elements
    draw_moana()
    draw_arrows()
    draw_animals()
    draw_treasures()
    draw_boat() # Draw the boat if spawned
    
    # Display game info
    glColor3f(1.0, 1.0, 0.8)  # Light yellow text
    draw_text(10, 770, f"Moana's Life: {moana_life}")
    draw_text(10, 740, f"Arrows Left: {arrows_left}")
    draw_text(10, 710, f"Missed Arrows: {arrows_missed}")
    draw_text(10, 680, f"Score: {score}")

    # Draw water bottles
    glColor3f(0.0, 0.7, 1.0)  # Light blue for water
    draw_text(10, 650, f"Water Bottles: {water_bottles}/{MAX_WATER_BOTTLES}")
    
    # Draw bottle icons
    bottle_width = 15
    bottle_height = 25
    bottle_spacing = 20
    bottle_y = 620
    
    for i in range(MAX_WATER_BOTTLES):
        bottle_x = 10 + i * bottle_spacing
        
        # Draw bottle outline
        if i < water_bottles:
            # Filled bottle
            glColor3f(0.0, 0.7, 1.0)  # Blue for filled bottles
            
            # Draw bottle body
            glBegin(GL_QUADS)
            glVertex2f(bottle_x, bottle_y)
            glVertex2f(bottle_x + bottle_width, bottle_y)
            glVertex2f(bottle_x + bottle_width, bottle_y - bottle_height)
            glVertex2f(bottle_x, bottle_y - bottle_height)
            glEnd()
            
            # Draw bottle cap
            glColor3f(0.5, 0.5, 0.5)  # Gray cap
            glBegin(GL_QUADS)
            glVertex2f(bottle_x + 3, bottle_y + 5)
            glVertex2f(bottle_x + bottle_width - 3, bottle_y + 5)
            glVertex2f(bottle_x + bottle_width - 3, bottle_y)
            glVertex2f(bottle_x + 3, bottle_y)
            glEnd()
        else:
            # Empty bottle (outline only)
            glColor3f(0.5, 0.5, 0.5)  # Gray for empty bottles
            
            # Draw bottle outline
            glBegin(GL_LINE_LOOP)
            glVertex2f(bottle_x, bottle_y)
            glVertex2f(bottle_x + bottle_width, bottle_y)
            glVertex2f(bottle_x + bottle_width, bottle_y - bottle_height)
            glVertex2f(bottle_x, bottle_y - bottle_height)
            glEnd()
            
            # Draw bottle cap outline
            glBegin(GL_LINE_LOOP)
            glVertex2f(bottle_x + 3, bottle_y + 5)
            glVertex2f(bottle_x + bottle_width - 3, bottle_y + 5)
            glVertex2f(bottle_x + bottle_width - 3, bottle_y)
            glVertex2f(bottle_x + 3, bottle_y)
            glEnd()
    
    current_time = time.time()
    time_left = max(0, GAME_DURATION - (current_time - game_start_time))
    minutes = int(time_left // 60)
    seconds = int(time_left % 60)
    draw_text(10, 590, f"Time Left: {minutes:02d}:{seconds:02d}")
    
    if reloading:
        reload_progress = min(1, (current_time - reload_start_time) / RELOAD_TIME)
        draw_text(400, 700, f"Reloading: {int(reload_progress * 100)}%")
    
    if game_over:
        glColor3f(1.0, 0.3, 0.3)  # Red text
        draw_text(400, 400, "GAME OVER!", GLUT_BITMAP_HELVETICA_18)
        draw_text(400, 350, f"Final Score: {score}", GLUT_BITMAP_HELVETICA_18)
        draw_text(400, 300, "Press R to restart", GLUT_BITMAP_HELVETICA_18)
    
    if game_won:
        glColor3f(0.3, 1.0, 0.3)  # Green text
        draw_text(400, 400, "VICTORY!", GLUT_BITMAP_HELVETICA_18)
        draw_text(400, 350, f"Final Score: {score}", GLUT_BITMAP_HELVETICA_18)
        draw_text(400, 300, "Press R to play again", GLUT_BITMAP_HELVETICA_18)


        # Display fetch water message for 5 seconds
    if fetch_message and (current_time - fetch_message_start_time <= 5):
        glColor3f(1.0, 1.0, 0.0)  # Yellow text
        draw_text(400, 200, fetch_message, GLUT_BITMAP_HELVETICA_18)
    elif current_time - fetch_message_start_time > 5:
        fetch_message = ""  # Clear the message after 5 seconds

    glutSwapBuffers()

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
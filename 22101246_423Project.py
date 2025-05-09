from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time
from math import sin, cos, radians

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




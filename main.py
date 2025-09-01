import pygame
from sys import exit, stdout
import random
import math
import numpy as np
import logging
import numba
import time as tm
import prey
import predator
import plotting

global width, height
width, height = 1800, 1200  # Set the dimensions of the simulation window

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(stdout)
logger.addHandler(stream_handler)

# Function to draw food on the screen
def draw_food(screen, food):
    for f in food:
        pygame.draw.circle(screen, (255, 255, 0), tuple(f), 5)  # Draw food as yellow circles

# Function to generate food
def generate_food(food):
    # Randomly generate new food items
    for i in range(0 if random.randint(0, 100) > 30 else 1): # 30% chance to generate new food
        new_food = np.array([(random.randint(0, width), random.randint(0, height))])
        food = np.vstack([food, new_food])
    return food

def eat_food(food, preys, total_prey_created):
    remove_indices = []
    new_preys = []
    for p in preys:
        if p.closest_food is not None:
            dist = np.linalg.norm(np.array([p.x, p.y]) - p.closest_food)
            if dist < 25:
                matches = np.where((food == p.closest_food).all(axis=1))[0]
                if matches.size > 0:
                    logger.debug(f"Prey at ({p.x}, {p.y}) has eaten food at {tuple(p.closest_food)} and reproduced!")
                    idx = matches[0]
                    remove_indices.append(idx)
                    p.hunger += 3
                    # Reproduce immediately for this prey
                    new_preys.append(prey.Prey(
                        p.x,
                        p.y,
                        (p.direction + random.uniform(math.pi/2, 3*math.pi/2)) % (2 * math.pi),  # Reverse direction
                        p.speed,
                        p.turning_rate,
                        (max(0, min(p.colour[0] + random.randint(-50, 50), 255)),
                         max(0, min(p.colour[1] + random.randint(-50, 50), 255)),
                         max(0, min(p.colour[2] + random.randint(-50, 50), 255))),
                        total_prey_created
                    ))
                    total_prey_created += 1

    if remove_indices:
        food = np.delete(food, remove_indices, axis=0)
    if new_preys:
        preys.add(*new_preys)
    return food, total_prey_created

def eat_prey(predators, preys):
    new_predators = []
    for pred in predators:
        if pred.closest_prey is not None:
            dist = np.linalg.norm(np.array([pred.x, pred.y]) - np.array([pred.closest_prey[0], pred.closest_prey[1]]))
            if dist < 20:
                matches = [p for p in preys if p.id == pred.closest_prey_id]
                if len(matches) > 0:
                    logger.debug(f"A predator at ({pred.x}, {pred.y}) has eaten a prey at {tuple(pred.closest_prey)} and reproduced!")
                    prey_to_eat = matches[0]
                    preys.remove(prey_to_eat)
                    pred.hunger += 1
                    pred.closest_prey = None
                    new_predators.append(predator.Predator(
                        pred.x,
                        pred.y,
                        (pred.direction + math.pi) % (2 * math.pi),  # Reverse direction
                        pred.speed,
                        pred.turning_rate,
                        (max(0, min(pred.colour[0] + random.randint(-50, 50), 255)),
                        max(0, min(pred.colour[1] + random.randint(-50, 50), 255)),
                        max(0, min(pred.colour[2] + random.randint(-50, 50), 255)))
                    ))

    if new_predators:
        predators.add(*new_predators)
    return preys

# Function to remove starved preys
def remove_starved_preys(preys):
    for p in preys:
        p.hunger -= 1 # Decrease hunger every second
        if p.hunger <= 0: # If hunger reaches zero, remove the prey
            preys.remove(p)
            logger.debug(f"A prey at ({p.x}, {p.y}) has starved to death.")
    return preys

def removed_starved_predators(predators):
    for p in predators:
        p.hunger -= 1 # Decrease hunger every second
        if p.hunger <= 0: # If hunger reaches zero, remove the predator
            predators.remove(p)
            logger.debug(f"A predator at ({p.x}, {p.y}) has starved to death.")
    return predators

# Numba-accelerated function to find the closest food for each prey
@numba.njit
def find_closest_entity_batch(eater_positions, food_positions, detection_radius):
    # eater_info is expected to be a 2D np.array of shape (n, 3) where each row is (x, y, food_detection_radius)
    # food_positions is expected to be a 2D np.array of shape (m, 2) where each row is (x, y)
    n_prey = eater_positions.shape[0]
    closest_indices = -np.ones(n_prey, dtype=np.int64)
    for i in range(n_prey):
        diffs = food_positions - eater_positions[i]
        dists = np.sqrt((diffs ** 2).sum(axis=1))
        within_radius = np.where(dists < detection_radius)[0]
        if within_radius.size > 0:
            idx = within_radius[np.argmin(dists[within_radius])]
            closest_indices[i] = idx
    return closest_indices

    
# Main function to run the simulation
def main():
    pygame.init()
    
    # Set up the display
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Predator and Prey Simulation")
    pygame.display.set_icon(pygame.image.load("icon.png"))  # Loads icon

    # Set up clock and FPS
    clock = pygame.time.Clock()
    fps = 30
    counter = 0
    time = 0

    total_prey_created = 20

    #Initialize start position and attributes for the simulation
    # Generate initial food
    food = np.array([(random.randint(0, width), random.randint(0, height)) for i in range(40)])

    # Initialize prey
    preys = pygame.sprite.Group(
        prey.Prey(
        random.randint(0, width), #x
        random.randint(0, height), #y
        random.uniform(0, math.pi), #direction 
        3.0, #speed
        0.05, #turning_rate
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), #colour
        i+1)  # Unique ID for each prey 
        for i in range(total_prey_created)
        )
    
    # Initialize predators
    predators = pygame.sprite.Group(
        predator.Predator(
        random.randint(0, width), #x
        random.randint(0, height), #y
        random.uniform(0, math.pi), #direction
        3.0, #speed
        0.05, #turning_rate
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))) #colour
        for i in range(15)
        )

    logger.debug("Simulation started.")
    # Main loop
    running = True
    while running:
        t0 = tm.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen with a color
        screen.fill((0, 0, 0))  # Fill with black

        # Generate food
        food = generate_food(food)
        
        # Calculate closest food and predators for each prey using batch processing
        if predators and preys: # Both predators and preys exist
            closest_predator_indices = find_closest_entity_batch(np.array([[p.x, p.y] for p in preys]), np.array([[pred.x, pred.y] for pred in predators]), 200)
            closest_prey_indices = find_closest_entity_batch(np.array([[pred.x, pred.y] for pred in predators]), np.array([[p.x, p.y] for p in preys]), 400)
            closest_food_indices = find_closest_entity_batch(np.array([[p.x, p.y] for p in preys]), food, 200)
        elif preys: # No predators
            closest_food_indices = find_closest_entity_batch(np.array([[p.x, p.y] for p in preys]), food, 200)
            closest_predator_indices = -np.ones(len(preys), dtype=np.int64)
            closest_prey_indices = np.array([])
        elif predators: # No preys
            closest_predator_indices = np.array([])
            closest_prey_indices = -np.ones(len(predators), dtype=np.int64)
            closest_food_indices = np.array([])
        else: # No preys or predators
            closest_predator_indices = np.array([])
            closest_prey_indices = np.array([])
            closest_food_indices = np.array([])
        
        # Update closest food and predators for each prey
        for i, p in enumerate(preys):
            if closest_food_indices[i] != -1:
                p.closest_food = food[closest_food_indices[i]]
            else:
                p.closest_food = None

            if closest_predator_indices[i] != -1:
                p.closest_predator = np.array([predators.sprites()[closest_predator_indices[i]].x, predators.sprites()[closest_predator_indices[i]].y])
            else:
                p.closest_predator = None

        # Update closest prey for each predator
        for i, pred in enumerate(predators):
            if closest_prey_indices[i] != -1:
                prey_found = preys.sprites()[closest_prey_indices[i]]
                pred.closest_prey = np.array([prey_found.x, prey_found.y])
                pred.closest_prey_id = prey_found.id
            else:
                pred.closest_prey = None
                pred.closest_prey_id = None


        # Move preys and predators
        preys.update()
        predators.update()

        # Handle eating food
        food, total_prey_created = eat_food(food, preys, total_prey_created)
        preys = eat_prey(predators, preys)

        clock.tick(fps)
        counter += 1
        # Handles hunger decrease and starvation every 30 frames
        if counter == 30:
            counter = 0
            time += 1
            #remove_starved_preys(preys)
            #plotting.record_time(time)
            #plotting.gather_population_data(len(preys), len(predators))
            #plotting.gather_speed_data(preys, predators)
            #plotting.gather_turning_rate_data(preys, predators)
        elif counter == 15:
            removed_starved_predators(predators)

        # Update the display
        draw_food(screen, food)
        preys.draw(screen)
        predators.draw(screen)
        pygame.display.flip()
        t1 = tm.time()
        logger.debug(f"Frame time: {t1 - t0} seconds")

    pygame.quit()
    #plotting.plot_population_data()
    #plotting.plot_speed_data()
    #plotting.plot_turning_rate_data()
    logger.info("Simulation ended.")
    exit()

if __name__ == "__main__":
    main()

"""
To do list:
-Record and plot population and trait data
-Multiprocessing for performance?
-Use variables for prey and predator attributes for easier tuning
"""
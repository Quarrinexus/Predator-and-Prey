import pygame
from sys import exit
import random
import math
import numpy as np
import logging
import prey
import predator
import plotting

global width, height
width, height = 2200, 1200  # Set the dimensions of the simulation window

# Function to draw food on the screen
def draw_food(screen, food):
    for f in food:
        pygame.draw.circle(screen, (255, 255, 0), (int(f[0]), int(f[1])), 5)  # Draw food as yellow circles

# Function to generate food
def generate_food(food):
    # Randomly generate new food items
    for i in range(0 if random.randint(0, 100) > 10 else 1): # 10% chance to generate new food
        new_food = np.array((random.randint(0, width), random.randint(0, height)))
        food = np.vstack([food, new_food])
    return food

def eat_food(food, preys):
    remove_indices = []
    new_preys = []
    for p in preys:
        if p.closest_food is not None:
            dist = np.linalg.norm(np.array([p.x, p.y]) - p.closest_food)
            if dist < 25:
                matches = np.where((food == p.closest_food).all(axis=1))[0]
                if matches.size > 0:
                    idx = matches[0]
                    remove_indices.append(idx)
                    p.hunger += 5
                    p.closest_food = None
                    # Reproduce immediately for this prey
                    new_preys.append(prey.Prey(
                        p.x,
                        p.y,
                        (p.direction + math.pi) % (2 * math.pi),
                        p.speed * random.uniform(0.8, 1.2),
                        p.turning_rate * random.uniform(0.8, 1.2),
                        p.food_detection_radius * random.uniform(0.8, 1.2),
                        p.predator_detection_radius * random.uniform(0.8, 1.2),
                        (max(0, min(p.colour[0] + random.randint(-50, 50), 255)),
                         max(0, min(p.colour[1] + random.randint(-50, 50), 255)),
                         max(0, min(p.colour[2] + random.randint(-50, 50), 255)))
                    ))

    if remove_indices:
        food = np.delete(food, remove_indices, axis=0)
    if new_preys:
        preys.add(*new_preys)
    return food

def eat_prey(predators, preys):
    new_predators = []
    for pred in predators:
        pred.find_closest_prey([np.array([p.x, p.y]) for p in preys])
        if pred.closest_prey is not None:
            dist = np.linalg.norm(np.array([pred.x, pred.y]) -
                                  np.array([pred.closest_prey[0], pred.closest_prey[1]]))
            if dist < 30:
                matches = [p for p in preys if (p.x, p.y) == tuple(pred.closest_prey)]
                if len(matches) > 0:
                    prey_to_eat = matches[0]
                    preys.remove(prey_to_eat)
                    pred.hunger += 5
                    pred.closest_prey = None
                    new_predators.append(predator.Predator(
                        pred.x,
                        pred.y,
                        (pred.direction + math.pi) % (2 * math.pi),
                        pred.speed * random.uniform(0.8, 1.2),
                        pred.turning_rate * random.uniform(0.8, 1.2),
                        pred.prey_detection_radius * random.uniform(0.8, 1.2),
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
    return preys

def removed_starved_predators(predators):
    for p in predators:
        p.hunger -= 1 # Decrease hunger every second
        if p.hunger <= 0: # If hunger reaches zero, remove the predator
            predators.remove(p)
    return predators

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

    # Set up population history arrays
    prey_population_data = [10]
    predator_population_data = [5]
    times = [0]

    # Set up logger
    #logger = logging.Logger()

    #Initialize start position and attributes for the simulation
    food = np.array([(random.randint(0, width), random.randint(0, height)) for i in range(75)])
    preys = pygame.sprite.Group(
        prey.Prey(
        random.randint(0, width), #x
        random.randint(0, height), #y
        random.uniform(0, math.pi), #direction 
        random.uniform(3.0, 5.0), #speed
        random.uniform(0.1, 0.15), #turning_rate
        random.randint(100, 200), #food_detection_radius
        random.randint(50, 100), #predator_detection_radius
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), #colour
        ) for i in range(15))
    predators = pygame.sprite.Group(
        predator.Predator(
        random.randint(0, width), #x
        random.randint(0, height), #y
        random.uniform(0, math.pi), #direction
        random.uniform(3.0, 5.0), #speed
        random.uniform(0.1, 0.15), #turning_rate
        random.randint(300, 500), #prey_detection_radius
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) #colour
        ) for i in range(5))

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Fill the screen with a color
        screen.fill((0, 0, 0))  # Fill with black

        # Generate food
        food = generate_food(food)

        # Recalculate closest food for each prey
        if counter % 10 == 0:
            for p in preys:
                p.find_closest_food(food)
        # stagger predator prey detection
        elif counter % 10 == 5:
            preys = eat_prey(predators, preys)

        # Move preys and predators
        preys.update()
        predators.update()

        # Handle eating food
        food = eat_food(food, preys)

        clock.tick(fps)
        counter += 1
        # Handles hunger decrease and starvation every 30 frames
        if counter == 30:
            counter = 0
            time += 1
            remove_starved_preys(preys)
            prey_population_data.append(len(preys))
            predator_population_data.append(len(predators))
            times.append(time)
        elif counter == 15:
            removed_starved_predators(predators)

        # Update the display
        draw_food(screen, food)
        preys.draw(screen)
        predators.draw(screen)
        pygame.display.flip()

    pygame.quit()
    plotting.plot_population_data(prey_population_data, predator_population_data, times)
    exit()

if __name__ == "__main__":
    main()

"""
To do list:
-Create Logger
-Create ID system and use it to make predators eat prey more cleanly
-Create prey running AI
-Record and plot population and trait data
"""
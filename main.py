import pygame
from sys import exit
import random
import math
import numpy as np
import prey
import predator

# Function to draw food on the screen
def draw_food(screen, food):
    for f in food:
        pygame.draw.circle(screen, (255, 255, 0), (int(f[0]), int(f[1])), 5)  # Draw food as yellow circles

# Function to generate food
def generate_food(food):
    # Randomly generate new food items
    for i in range(0 if random.randint(0, 100) > 4 else 1): # 4% chance to generate new food
        new_food = np.array((random.randint(0, 2200), random.randint(0, 1200)))
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
                         max(0, min(p.colour[2] + random.randint(-50, 50), 255))    
                    )))

    if remove_indices:
        food = np.delete(food, remove_indices, axis=0)
    if new_preys:
        preys.add(*new_preys)
    return food

# Function to remove starved preys
def remove_starved_preys(preys):
    for p in preys:
        p.hunger -= 1 # Decrease hunger every second
        if p.hunger <= 0: # If hunger reaches zero, remove the prey
            preys.remove(p)
            print(f"Removed starved prey at ({p.x}, {p.y})")
    return preys

# Main function to run the simulation
def main():
    pygame.init()
    
    # Set up the display
    width, height = 2200, 1200
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Predator and Prey Simulation")
    pygame.display.set_icon(pygame.image.load("icon.png"))  # Loads icon

    # Set up clock and FPS
    clock = pygame.time.Clock()
    fps = 30
    counter = 0

    #Initialize start position and attributes for the simulation
    food = np.array([(random.randint(0, 2200), random.randint(0, 1200)) for i in range(75)])
    preys = pygame.sprite.Group(
        prey.Prey(
        random.randint(0, 2200), #x
        random.randint(0, 1200), #y
        random.uniform(0, math.pi), #direction 
        random.uniform(3.0, 5.0), #speed
        random.uniform(0.1, 0.15), #turning_rate
        random.randint(100, 200), #food_detection_radius
        random.randint(100, 200), #predator_detection_radius
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) #colour
        ) for i in range(10))
    for p in preys:
        print(p)  # Debugging output to check prey initialization
    predators = []

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

        # Move preys and predators
        preys.update()

        # Handle eating food
        food = eat_food(food, preys)

        clock.tick(fps)
        counter += 1
        # Handles hunger decrease every 30 frames
        if counter == 30:
            counter = 0
            remove_starved_preys(preys)

        # Update the display
        draw_food(screen, food)
        preys.draw(screen)
        pygame.display.flip()

    pygame.quit()
    exit()

if __name__ == "__main__":
    main()
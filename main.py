import pygame
from sys import exit
import random
import math
import numpy as np
import prey
import predator

def draw_food(screen, food):
    for f in food:
        pygame.draw.circle(screen, (255, 255, 0), (int(f[0]), int(f[1])), 5)  # Draw food as yellow circles

def generate_food(food):
    for i in range(0 if random.randint(0, 100) > 4 else 1):
        new_food = np.array((random.randint(0, 2200), random.randint(0, 1200)))
        food = np.vstack([food, new_food])
    return food

def eat_food(food, preys):
    remove_indices = []
    for p in preys:
        if p.closest_food is not None:
            dist = np.linalg.norm(np.array([p.x, p.y]) - p.closest_food)
            if dist < 25:  # 25 pixels is a reasonable "eating" radius
                # Find index of closest_food in food array
                matches = np.where((food == p.closest_food).all(axis=1))[0]
                if matches.size > 0:
                    idx = matches[0]
                    remove_indices.append(idx)
                    p.hunger += 10
                    p.closest_food = None  # Reset closest food after eating
    if remove_indices:
        food = np.delete(food, remove_indices, axis=0)
    return food

def remove_starved_preys(preys):
    for p in preys:
        p.hunger -= 1
        if p.hunger <= 0:
            preys.remove(p)
            print(f"Removed starved prey at ({p.x}, {p.y})")
    return preys

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
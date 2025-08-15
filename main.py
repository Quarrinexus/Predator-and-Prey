import pygame
from sys import exit
import random
import math
import prey
import predator

def draw_food(screen, food):
    for f in food:
        pygame.draw.circle(screen, (255, 255, 0), f, 5)  # Draw food as yellow circles

def generate_food(food):
    for i in range(0 if random.randint(0, 100) > 4 else 1):
        food.append((random.randint(0, 2200), random.randint(0, 1200)))

def eat_food(food, preys):
    for p in preys:
        if p.closest_food:
            dist = math.hypot(p.x - p.closest_food[0], p.y - p.closest_food[1])
            if dist < 20:  # 20 pixels is a reasonable "eating" radius
                if p.closest_food in food:
                    food.remove(p.closest_food)
                    p.hunger += 10
                    p.closest_food = None  # Reset closest food after eating

def main():
    pygame.init()
    
    # Set up the display
    width, height = 2200, 1200
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Predator and Prey Simulation")

    # Set up clock and FPS
    clock = pygame.time.Clock()
    fps = 30
    counter = 0

    #Initialize start position and attributes for the simulation
    food = [(random.randint(0, 2200), random.randint(0, 1200)) for i in range(50)]
    
    preys = pygame.sprite.Group(
        prey.Prey(
        random.randint(0, 2200), #x
        random.randint(0, 1200), #y
        random.uniform(0, math.pi), #direction 
        random.uniform(0.1, 0.5), #speed
        random.uniform(0.05, 0.1), #turning_rate
        random.randint(50, 200), #food_detection_radius
        random.randint(50, 200), #predator_detection_radius
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) #colour
        ) for i in range(10)
        )
    """
    preys = [prey.Prey(
        random.randint(0, 2200), #x
        random.randint(0, 1200), #y
        random.uniform(0, math.pi), #direction 
        random.uniform(1, 5), #speed
        random.uniform(0.05, 0.1), #turning_rate
        random.randint(300, 600), #food_detection_radius
        random.randint(50, 200), #predator_detection_radius
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) #colour
        )]
    """
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
        generate_food(food)

        # Move preys and predators
        preys.update(food, predators)

        # Handle eating food
        eat_food(food, preys)

        # Update the display
        draw_food(screen, food)
        preys.draw(screen)
        pygame.display.flip()
        clock.tick(fps)
        counter += 1
        if counter == 60:
            counter = 0

    pygame.quit()
    exit()

if __name__ == "__main__":
    main()
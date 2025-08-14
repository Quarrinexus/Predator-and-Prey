import pygame
from sys import exit
import random
import math
import prey
import predator

#Initialize start position and attributes for the simulation
food = [(random.randint(0, 2200), random.randint(0, 1200)) for i in range(50)]
preys = [prey.Prey(
    random.randint(0, 2200), #x
    random.randint(0, 1200), #y
    random.uniform(0, math.pi), #direction 
    random.uniform(0.1, 0.5), #speed
    random.uniform(0.05, 0.1), #turning_rate
    random.randint(50, 200), #food_detection_radius
    random.randint(50, 200), #predator_detection_radius
    (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)) #colour
    ) for i in range(10)]
#predators = []

def draw_food(screen):
    for f in food:
        pygame.draw.circle(screen, (255, 255, 0), f, 5)  # Draw food as yellow circles

def draw_preys(screen):
    for p in preys:
        p.draw(screen)

def main():
    pygame.init()
    
    # Set up the display
    width, height = 2200, 1200
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Predator and Prey Simulation")

    # Set up clock and FPS
    clock = pygame.time.Clock()
    fps = 60

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Generate new food randomly
        for i in range(0 if random.randint(0, 100) > 4 else 1):
            food.append((random.randint(0, 2200), random.randint(0, 1200)))


        # Fill the screen with a color
        screen.fill((0, 0, 0))  # Fill with black

        # Update the display
        draw_food(screen)
        draw_preys(screen)
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()
    exit()

if __name__ == "__main__":
    main()
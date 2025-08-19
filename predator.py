import pygame
import math
import numpy as np

global width, height
width, height = 1800, 800  # Set the dimensions of the simulation

class Predator(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, turning_rate, prey_detection_radius, colour):
        super().__init__()
        #initial position variables
        self.x = x
        self.y = y
        self.direction = direction

        #attributes for movement and behaviour
        self.speed = speed
        self.turning_rate = turning_rate
        self.prey_detection_radius = prey_detection_radius
        self.hunger = 4
        self.closest_prey = None
        self.closest_prey_id = None

        #attributes for appearance (predator is a triangle)
        self.colour = colour
        self.base_image = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.polygon(self.base_image, self.colour, [(20, 30), (0, 60), (40, 60)])
        self.image = pygame.transform.rotate(self.base_image, math.degrees(self.direction))
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def __repr__(self):
        return f"Predator(x={self.x}, y={self.y}, direction={self.direction}, speed={self.speed}, closest_prey={self.closest_prey})"
    
    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 3)
        pygame.draw.rect(self.base_image, (255, 255, 0), self.base_image.get_rect(), 1)

    def find_closest_prey(self, prey):
        # NumPy optimization: prey is expected to be a 2D np.array of shape (n, 2)
        if len(prey) == 0:
            self.closest_prey = None
            return
        pos = np.array([self.x, self.y])
        prey_positions = prey[:, :2]  # Extract only the x, y coordinates
        dists = np.linalg.norm(prey_positions - pos, axis=1)
        within_radius = np.where(dists < self.prey_detection_radius)[0]
        if within_radius.size > 0:
            idx = within_radius[np.argmin(dists[within_radius])]
            self.closest_prey = prey_positions[idx]
            self.closest_prey_id = prey[idx, 2]  # Assuming prey has an id in the third column
        else:
            self.closest_prey = None
            self.closest_prey_id = None

    def update(self):
        # angle to closest food
        if self.closest_prey is not None:
            direction_to_prey = math.atan2(self.closest_prey[1] - self.y, self.closest_prey[0] - self.x)
            angle_diff = (direction_to_prey - self.direction + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turning_rate:
                self.direction += self.turning_rate * (1 if angle_diff > 0 else -1)
            else:
                self.direction = direction_to_prey

        # Rotate the image to face the direction
        pygame.draw.polygon(self.base_image, self.colour, [(20, 20), (0, 60), (40, 60)])
        self.image = pygame.transform.rotate(self.base_image, -math.degrees(self.direction + math.pi/2))

        # Move the prey in the current direction
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.x = max(0, min(self.x, width))  # Keep within bounds
        self.y = max(0, min(self.y, height))
        self.rect.center = (self.x, self.y)
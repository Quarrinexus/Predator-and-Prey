import pygame
import math
import numpy as np

global width, height
width, height = 1800, 1200  # Set the dimensions of the simulation

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

    def update(self):
        # free space to implement neural network decision making later

        # Rotate the image to face the direction
        pygame.draw.polygon(self.base_image, self.colour, [(20, 20), (0, 60), (40, 60)])
        self.image = pygame.transform.rotate(self.base_image, -math.degrees(self.direction + math.pi/2))

        # Move the prey in the current direction
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.x = max(0, min(self.x, width))  # Keep within bounds
        self.y = max(0, min(self.y, height))
        self.rect.center = (self.x, self.y)
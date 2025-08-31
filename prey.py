import pygame
import math
import numpy as np
import random

global width, height
width, height = 1800, 1200  # Set the dimensions of the simulation

class Prey(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, turning_rate, food_detection_radius, predator_detection_radius, colour, id):
        super().__init__()
        #initial position variables
        self.x = x
        self.y = y
        self.direction = direction
        self.id = id

        #attributes for movement and behaviour
        self.speed = speed
        self.turning_rate = turning_rate
        self.food_detection_radius = food_detection_radius
        self.predator_detection_radius = predator_detection_radius
        self.hunger = 8
        self.closest_food = None
        self.closest_predator = None

        #attributes for appearance
        self.colour = colour
        self.image = pygame.Surface((40, 40))
        self.image.fill(colour)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def __repr__(self):
        return f"Prey(id = {self.id}, x={self.x}, y={self.y}, direction={self.direction}, speed={self.speed}, colour={self.colour}), closest_food={self.closest_food})"

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 3)

    def update(self):
        # free space to implement neural network decision making later

        # Move the prey in the current direction
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.x = max(0, min(self.x, width))  # Keep within bounds
        self.y = max(0, min(self.y, height))
        self.rect.center = (self.x, self.y)
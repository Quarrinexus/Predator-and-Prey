import pygame
import math
import numpy as np
from brain import Brain

global width, height
width, height = 1800, 1200  # Set the dimensions of the simulation

class Prey(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, turning_rate, colour, hunger=8.0, fitness=0, parent=None):
        super().__init__()
        #initial position variables
        self.x = x
        self.y = y
        self.direction = direction
        self.id = id

        #attributes for movement and behaviour
        self.speed = speed
        self.turning_rate = turning_rate
        self.hunger = hunger
        self.max_hunger = 16.0
        self.closest_food = None
        self.closest_predator = None
        self.closest_predator_direction = 0.0

        self.fitness = fitness # Number of food items eaten
        self.brain = Brain(input_size=7, hidden_size=16, output_size=1, parent_brain=None if parent is None else parent.brain)

        #attributes for appearance
        self.colour = colour
        self.image = pygame.Surface((40, 40))
        self.image.fill(colour)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def __repr__(self):
        return f"Prey(x={self.x}, y={self.y}, direction={self.direction}, closest_food={self.closest_food})"

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 255, 0), (int(self.x), int(self.y)), 3)

    def update(self):
        # neural network decision making
        if self.closest_food is not None:
            dx_food = self.closest_food[0] - self.x
            dy_food = self.closest_food[1] - self.y
            distance_to_food = math.hypot(dx_food, dy_food) / 200
            angle_to_food = math.atan2(dy_food, dx_food) - self.direction
            angle_to_food = (angle_to_food + math.pi) % (2 * math.pi) - math.pi
        else:
            distance_to_food = 1.0
            angle_to_food = 0.0

        if self.closest_predator is not None:
            dx_pred = self.closest_predator[0] - self.x
            dy_pred = self.closest_predator[1] - self.y
            distance_to_predator = math.hypot(dx_pred, dy_pred) / 200
            angle_to_predator = math.atan2(dy_pred, dx_pred) - self.direction
            angle_to_predator = (angle_to_predator + math.pi) % (2 * math.pi) - math.pi
        else:
            distance_to_predator = -1.0
            angle_to_predator = 0.0
            self.closest_predator_direction = 0.0

        input_vector = np.array([
            distance_to_food,
            angle_to_food,
            distance_to_predator,
            angle_to_predator,
            self.closest_predator_direction / math.pi, # Normalize angle to -1..1
            self.direction / math.pi,  # Normalize angle to -1..1
            self.hunger / self.max_hunger
        ])
        input_vector = input_vector.reshape((1, 7)) # Reshape for neural network input
        output = self.brain.forward(input_vector)
        change_in_direction = output[0][0] * self.turning_rate
        self.direction = (self.direction + change_in_direction + math.pi) % (2 * math.pi) - math.pi

        # Move the prey in the current direction
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.x = max(0, min(self.x, width))  # Keep within bounds
        self.y = max(0, min(self.y, height))
        self.rect.center = (self.x, self.y)
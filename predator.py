import pygame
import math
import numpy as np
from brain import Brain

global width, height
width, height = 1800, 1200  # Set the dimensions of the simulation

class Predator(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, turning_rate, colour, parent=None):
        super().__init__()
        #initial position variables
        self.x = x
        self.y = y
        self.direction = direction

        #attributes for movement and behaviour
        self.speed = speed
        self.turning_rate = turning_rate
        self.hunger = 6
        self.max_hunger = 16
        self.closest_prey = None
        self.closest_prey_direction = None
        self.closest_prey_id = None

        self.fitness = 0 # Number of prey caught
        self.brain = Brain(input_size=5, hidden_size=16, output_size=1, parent_brain=None if parent is None else parent.brain)

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
        # neural network decision making
        if self.closest_prey is not None:
            dx_prey = self.closest_prey[0] - self.x
            dy_prey = self.closest_prey[1] - self.y
            distance_to_prey = math.hypot(dx_prey, dy_prey) / 400 # 400 is the detectoin range
            angle_to_prey = math.atan2(dy_prey, dx_prey) - self.direction
            angle_to_prey = (angle_to_prey + math.pi) % (2 * math.pi) - math.pi
        else:
            distance_to_prey = -1.0
            angle_to_prey = 0.0

        input_vector = np.array([
            distance_to_prey,
            angle_to_prey / math.pi,  # Normalize angle to -1..1
            self.hunger / self.max_hunger,  # Normalize hunger to 0..1
            self.direction / math.pi, # Normalize direction to -1..1
            self.closest_prey_direction / math.pi
        ])
        input_vector = input_vector.reshape((1, 5))  # Reshape for neural network input
        output = self.brain.forward(input_vector)
        change_in_direction = output[0][0] * self.turning_rate
        self.direction = (self.direction + change_in_direction + math.pi) % (2 * math.pi) - math.pi


        # Rotate the image to face the direction
        pygame.draw.polygon(self.base_image, self.colour, [(20, 20), (0, 60), (40, 60)])
        self.image = pygame.transform.rotate(self.base_image, -math.degrees(self.direction + math.pi/2))

        # Move the prey in the current direction
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.x = max(0, min(self.x, width))  # Keep within bounds
        self.y = max(0, min(self.y, height))
        self.rect.center = (self.x, self.y)
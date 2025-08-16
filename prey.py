import pygame
import math
import numpy as np
import random

global width, height
width, height = 1800, 800  # Set the dimensions of the simulation

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

    def find_closest_food(self, food):
        # NumPy optimization: food is expected to be a 2D np.array of shape (n, 2)
        if len(food) == 0:
            self.closest_food = None
            return
        pos = np.array([self.x, self.y])
        dists = np.linalg.norm(food - pos, axis=1)
        within_radius = np.where(dists < self.food_detection_radius)[0]
        if within_radius.size > 0:
            idx = within_radius[np.argmin(dists[within_radius])]
            self.closest_food = food[idx]
        else:
            self.closest_food = None

    def find_closest_predator(self, predators):
        # NumPy optimization: predators is expected to be a 2D np.array of shape (n, 2)
        if len(predators) == 0:
            self.closest_predator = None
            return
        pos = np.array([self.x, self.y])
        dists = np.linalg.norm(predators - pos, axis=1)
        within_radius = np.where(dists < self.predator_detection_radius)[0]
        if within_radius.size > 0:
            idx = within_radius[np.argmin(dists[within_radius])]
            self.closest_predator = predators[idx]
        else:
            self.closest_predator = None

    def update(self):
        # angle to closest food
        if self.closest_predator is not None:
            direction_from_predator = (math.atan2(self.closest_predator[1] - self.y, self.closest_predator[0] - self.x) + math.pi) % (2 * math.pi)
            angle_diff = (direction_from_predator - self.direction + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turning_rate:
                self.direction += self.turning_rate * (1 if angle_diff > 0 else -1)
            else:
                self.direction = direction_from_predator
        # If no predator is detected, follow food
        elif self.closest_food is not None:
            direction_to_food = math.atan2(self.closest_food[1] - self.y, self.closest_food[0] - self.x)
            angle_diff = (direction_to_food - self.direction + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turning_rate:
                self.direction += self.turning_rate * (1 if angle_diff > 0 else -1)
            else:
                self.direction = direction_to_food
        # If no food or predator is detected, wander randomly
        else:
            target_point = np.array([random.randint(width/8, 7*width/8), random.randint(height/8, 7*height/8)])
            direction_to_target = math.atan2(target_point[1] - self.y, target_point[0] - self.x)
            angle_diff = (direction_to_target - self.direction + math.pi) % (2 * math.pi) - math.pi
            if abs(angle_diff) > self.turning_rate:
                self.direction += self.turning_rate * (1 if angle_diff > 0 else -1)
            else:
                self.direction = direction_to_target

        # Move the prey in the current direction
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.x = max(0, min(self.x, width))  # Keep within bounds
        self.y = max(0, min(self.y, height))
        self.rect.center = (self.x, self.y)
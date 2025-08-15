import pygame
import math
from functools import reduce

class Prey(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, speed, turning_rate, food_detection_radius, predator_detection_radius, colour):
        super().__init__()
        #initial position variables
        self.x = x
        self.y = y
        self.direction = direction

        #attributes for movement and behaviour
        self.speed = speed
        self.turning_rate = turning_rate
        self.food_detection_radius = food_detection_radius
        self.predator_detection_radius = predator_detection_radius
        self.hunger = 20
        self.closest_food = None

        #attributes for appearance
        self.colour = colour
        self.image = pygame.Surface((40, 40))
        self.image.fill(colour)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def __repr__(self):
        return f"Prey(x={self.x}, y={self.y}, direction={self.direction}, speed={self.speed}, colour={self.colour}), closest_food={self.closest_food})"

    def draw(self, screen):
        screen.blit(self.image, (self.x-20, self.y-20))

    def update(self, food, predators):
        # Check for food within detection radius
        foods_in_radius = list(filter(lambda f: math.hypot(f[0] - self.x, f[1] - self.y) < self.food_detection_radius, food))
        self.closest_food = min(foods_in_radius, key=lambda f: math.hypot(f[0] - self.x, f[1] - self.y), default=None)
        
        # Direct towards closest food if available
        if self.closest_food is not None:
            direction_to_food = math.atan2(self.closest_food[1] - self.y, self.closest_food[0] - self.x)
            angle_diff = (direction_to_food - self.direction + math.pi) % (2 * math.pi) - math.pi  # shortest signed angle
            if abs(angle_diff) > self.turning_rate:
                self.direction += self.turning_rate * (1 if angle_diff > 0 else -1)
            else:
                self.direction = direction_to_food

        # Move the prey in the current direction
        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)
        self.x = max(0, min(self.x, 2200))  # Keep within bounds
        self.y = max(0, min(self.y, 1200))
        self.rect.center = (self.x, self.y)
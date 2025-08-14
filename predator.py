import pygame

class Predator:
    def __init__(self, x, y, direction, speed, turning_rate, food_find_radius, predator_detection_radius):
        #initial position variables
        self.x = x
        self.y = y
        self.direction = direction

        #attributes for movement and behaviour
        self.speed = speed
        self.turning_rate = turning_rate
        self.food_find_radius = food_find_radius
        self.predator_detection_radius = predator_detection_radius

        self.image = pygame.Surface((50, 50))  # Placeholder for predator image
        self.image.fill((255, 0, 0))  # Fill with red color for visibility

    def __repr__(self):
        return f"Predator(x={self.x}, y={self.y}, direction={self.direction}, speed={self.speed})"
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
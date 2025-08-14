import pygame

class Prey:
    def __init__(self, x, y, direction, speed, turning_rate, food_detection_radius, predator_detection_radius, colour):
        #initial position variables
        self.x = x
        self.y = y
        self.direction = direction

        #attributes for movement and behaviour
        self.speed = speed
        self.turning_rate = turning_rate
        self.food_detection_radius = food_detection_radius
        self.predator_detection_radius = predator_detection_radius

        #attributes for appearance
        self.colour = colour
        self.image = pygame.Surface((40, 40))
        self.image.fill(colour)

    def __repr__(self):
        return f"Prey(x={self.x}, y={self.y}, direction={self.direction}, speed={self.speed}, colour={self.colour})"

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        # Logic for prey movement can be added here
        pass
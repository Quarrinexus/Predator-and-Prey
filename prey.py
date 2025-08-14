import pygame

class Prey:
    def __init__(self, x, y, direction, speed, turning_rate, predator_detection_radius):
        #initial position variables
        self.x = x
        self.y = y
        self.direction = direction

        #attributes for movement and behaviour
        self.speed = speed
        self.turning_rate = turning_rate
        self.predator_detection_radius = predator_detection_radius
        self.image = pygame.Surface((20, 20))
        self.image.fill((0, 255, 0))  # Green color for prey

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def move(self):
        # Logic for prey movement can be added here
        pass
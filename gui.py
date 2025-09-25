import pygame
import numpy as np
import multiprocessing as mp

class Brain_GUI(mp.Process):
    def __init__(self, queue, width=1200, height=1000):
        super().__init__()

        # Multiprocessing queue to receive brain data
        self.queue = queue

        # Pygame window dimensions
        self.width = width
        self.height = height

        # Labels for input nodes
        self.prey_labels = ["Distance to Closest Food", "Angle to Closest Food", "Distance to Closest Pred", "Angle to Closest Pred", "Closest Pred Dir", "Current Direction", "Hunger"]
        self.predator_labels = ["Distance to Closest Prey", "Angle to Closest Prey", "Direction of Closest Prey", "Distance to Closest Food", "Angle to Closest Food", "Current Direction", "Hunger"]

    def draw_nodes(self, prey=True):
        # Draw input layer
        input_number = self.brain.W1.shape[0]
        for i in range(input_number):
            coords = (self.width * 2 / 10, (self.height * 0.4) * i / (input_number-1) + (self.height * 0.3))
            pygame.draw.circle(self.screen, (163, 217, 110), coords, 20)
            # Write labels besides circles
            label = self.prey_labels[i] if prey else self.predator_labels[i]
            text = self.font.render(label, True, (0, 0, 0))
            text_rect = text.get_rect(midright=(coords[0] - 25, coords[1]))
            self.screen.blit(text, text_rect)

        # Draw first hidden layer
        first_hidden_number = len(self.brain.b1)
        for i in range(first_hidden_number):
            coords = (self.width * 4 / 10, (self.height * 0.7) * i / (first_hidden_number-1) + (self.height * 0.15))
            pygame.draw.circle(self.screen, (114, 208, 230), coords, 20)
            # Write value onto circle
            value = f"{self.brain.b1[i]:.2f}"
            text = self.font.render(value, True, (0, 0, 0))
            text_rect = text.get_rect(center=coords)
            self.screen.blit(text, text_rect)

        # Draw second hidden layer
        second_hidden_number = len(self.brain.b2)
        for i in range(second_hidden_number):
            coords = (self.width * 7 / 10, (self.height * 0.7) * i / (second_hidden_number-1) + (self.height * 0.15))
            pygame.draw.circle(self.screen, (114, 208, 230), coords, 20)
            # Write value onto circle
            value = f"{self.brain.b2[i]:.2f}"
            text = self.font.render(value, True, (0, 0, 0))
            text_rect = text.get_rect(center=coords)
            self.screen.blit(text, text_rect)

        # Draw output layer
        coords = (self.width * 9 / 10, self.height / 2)
        pygame.draw.circle(self.screen, (217, 125, 125), coords, 20)
        # Write value onto circle
        value = f"{self.brain.b3[0]:.2f}"
        text = self.font.render(value, True, (0, 0, 0))
        text_rect = text.get_rect(center=coords)
        self.screen.blit(text, text_rect)

    def draw_layers(self):
        input_number = self.brain.W1.shape[0]
        first_hidden_number = len(self.brain.b1)
        second_hidden_number = len(self.brain.b2)

        # Get max absolute weights for scaling
        max_w1 = np.max(np.abs(self.brain.W1))
        max_w2 = np.max(np.abs(self.brain.W2))
        max_w3 = np.max(np.abs(self.brain.W3))

        # Draw input to first hidden layer
        for i in range(input_number):
            first_coord = (self.width * 2 / 10, (self.height * 0.4) * i / (input_number-1) + (self.height * 0.3))
            for j in range(first_hidden_number):
                second_coord = (self.width * 4 / 10, (self.height * 0.7) * j / (first_hidden_number-1) + (self.height * 0.15))
                weight = self.brain.W1[i, j]
                thickness = int(10 * abs(weight) / max_w1)
                pygame.draw.line(self.screen, (0, 0, 0) if self.brain.W1[i,j] > 0 else (100, 0, 0), first_coord, second_coord, thickness)

        # Draw first hidden to second hidden layer
        for i in range(first_hidden_number):
            first_coord = (self.width * 4 / 10, (self.height * 0.7) * i / (first_hidden_number-1) + (self.height * 0.15))
            for j in range(second_hidden_number):
                second_coord = (self.width * 7 / 10, (self.height * 0.7) * j / (second_hidden_number-1) + (self.height * 0.15))
                weight = self.brain.W2[i, j]
                thickness = int(10 * abs(weight) / max_w2)
                pygame.draw.line(self.screen, (0, 0, 0) if self.brain.W2[i,j] > 0 else (100, 0, 0), first_coord, second_coord, thickness)

        # Draw second hidden to output layer
        second_coord = (self.width * 9 / 10, self.height / 2)
        for i in range(second_hidden_number):
            first_coord = (self.width * 7 / 10, (self.height * 0.7) * i / (second_hidden_number-1) + (self.height * 0.15))
            weight = self.brain.W3[i, 0]
            thickness = int(10 * abs(weight) / max_w3)
            pygame.draw.line(self.screen, (0, 0, 0) if self.brain.W3[i, 0] > 0 else (100, 0, 0), first_coord, second_coord, thickness)

    def run(self):
        pygame.init()
        pygame.font.init()

        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.SysFont('Roboto Condensed', 14)
        pygame.display.set_caption("Neural Network Visualization")
        pygame.display.set_icon(pygame.image.load("brain.png"))
        self.brain = None

        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self.screen.fill((255, 255, 255))
            self.brain = self.queue.get()
            if self.brain == "QUIT": # Command to quit the GUI when the simulation ends
                break
            elif self.brain != None:
                self.draw_layers()
                self.draw_nodes()
            pygame.display.flip()
            clock.tick(1) # Limit to 1 FPS to reduce CPU usage
        pygame.quit()
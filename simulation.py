import pygame
from sys import stdout
import random
import math
import numpy as np
import logging
from numba import njit
import multiprocessing as mp
from prey import Prey
from predator import Predator

class Simulation(mp.Process):
    def __init__(self, brain_queue, population_queue, new_simulation=True, width=1800, height=1200):
        super().__init__()

        self.brain_queue = brain_queue
        self.population_queue = population_queue

        # Set up logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        stream_handler = logging.StreamHandler(stdout)
        self.logger.addHandler(stream_handler)

        self.width = width
        self.height = height

        # Load previous game state or start a new simulation
        if new_simulation:
            self.start_new_simulation()
        else:
            self.load_game_state()

    # Function to draw food on the screen
    def draw_food(self):
        for f in self.food:
            pygame.draw.circle(self.screen, (255, 255, 0), tuple(f), 5)  # Draw food as yellow circles

    # Function to generate food
    @staticmethod
    @njit
    def generate_food(food, width, height):
        if np.random.randint(0, 100) > 50:
            num_new = 0
        else:
            num_new = 1
        if num_new > 0:
            new_food = np.empty((num_new, 2), dtype=np.int64)
            for i in range(num_new):
                new_food[i, 0] = np.random.randint(0, width)
                new_food[i, 1] = np.random.randint(0, height)
            food = np.vstack((food, new_food))
        return food

    # Function to handle eating food and reproduction for prey
    def eat_food(self):
        remove_indices = []
        new_preys = []
        for prey in self.preys:
            if prey.closest_food is not None:
                dist = np.linalg.norm(np.array([prey.x, prey.y]) - prey.closest_food)
                if dist < 25:
                    matches = np.where((self.food == prey.closest_food).all(axis=1))[0]
                    if matches.size > 0:
                        idx = matches[0]
                        remove_indices.append(idx)
                        prey.hunger = min(prey.max_hunger, prey.hunger + 3.0)
                        prey.fitness += 1
                        # Reproduce immediately for this prey
                        new_preys.append(Prey(
                            prey.x,
                            prey.y,
                            (prey.direction + random.uniform(math.pi/2, 3*math.pi/2)) % (2 * math.pi),  # Spit out in opposite direction with some randomness
                            prey.speed,
                            prey.turning_rate,
                            (max(0, min(prey.colour[0] + random.randint(-50, 50), 255)),
                            max(0, min(prey.colour[1] + random.randint(-50, 50), 255)),
                            max(0, min(prey.colour[2] + random.randint(-50, 50), 255))),
                            parent=prey # parent of offspring
                        ))

        if remove_indices:
            self.food = np.delete(self.food, remove_indices, axis=0)
        if new_preys:
            self.preys.add(*new_preys)

    # Function to handle eating prey and reproduction for predators
    def eat_prey(self):
        new_predators = []
        for pred in self.predators:
            if pred.closest_prey is not None:
                dist = np.linalg.norm(np.array([pred.x, pred.y]) - np.array([pred.closest_prey[0], pred.closest_prey[1]]))
                if dist < 20:
                    matches = [prey for prey in self.preys if np.array_equal(np.array([prey.x, prey.y]), pred.closest_prey)]
                    if len(matches) > 0:
                        prey_to_eat = matches[0]
                        weakest_fittest = min(self.fittest_preys, key=lambda x: x.fitness, default=None)
                        if weakest_fittest is not None:
                            weakest_fittest_fitness = weakest_fittest.fitness
                            if prey_to_eat.fitness > weakest_fittest_fitness:
                                # Replace the weakest in fittest group
                                weakest_index = np.argmin([x.fitness for x in self.fittest_preys])
                                self.fittest_preys[weakest_index] = prey_to_eat
                        self.preys.remove(prey_to_eat)
                        pred.hunger = min(pred.max_hunger, pred.hunger + 3.0)
                        pred.fitness += 1
                        pred.closest_prey = None
                        new_predators.append(Predator(
                            pred.x,
                            pred.y,
                            (pred.direction + random.uniform(math.pi/2, 3*math.pi/2)) % (2 * math.pi),  # Spit out in opposite direction with some randomness
                            pred.speed,
                            pred.turning_rate,
                            (max(0, min(pred.colour[0] + random.randint(-50, 50), 255)),
                            max(0, min(pred.colour[1] + random.randint(-50, 50), 255)),
                            max(0, min(pred.colour[2] + random.randint(-50, 50), 255))),
                            parent=pred # Parent of offspring
                        ))

        if new_predators:
            self.predators.add(*new_predators)

    @staticmethod
    # Function to remove starved preys
    def remove_starved_entities(entities, fittest_group):
        to_remove = []
        for entity in list(entities):
            entity.hunger -= 1.0 # Decrease hunger every second
            if entity.hunger <= 0: # If hunger reaches zero, remove the prey
                to_remove.append(entity)
            weakest_fittest = min(fittest_group, key=lambda x: x.fitness, default=None)
            if weakest_fittest is not None:
                weakest_fittest_fitness = weakest_fittest.fitness
                if entity.fitness > weakest_fittest_fitness:
                    # Replace the weakest in fittest group
                    weakest_index = np.argmin([x.fitness for x in fittest_group])
                    fittest_group[weakest_index] = entity
                weakest_index = np.argmin([x.fitness for x in fittest_group])
                fittest_group[weakest_index] = entity
            entities.remove(entity)
        return entities, fittest_group

    # Numba-accelerated function to find the closest food for each prey
    @staticmethod
    @njit
    def find_closest_entity_batch(eater_positions, food_positions, detection_radius):
        # eater_info is expected to be a 2D np.array of shape (n, 3) where each row is (x, y, food_detection_radius)
        # food_positions is expected to be a 2D np.array of shape (m, 2) where each row is (x, y)
        n_prey = eater_positions.shape[0]
        closest_indices = -np.ones(n_prey, dtype=np.int64)
        for i in range(n_prey):
            diffs = food_positions - eater_positions[i]
            dists = np.sqrt((diffs ** 2).sum(axis=1))
            within_radius = np.where(dists < detection_radius)[0]
            if within_radius.size > 0:
                idx = within_radius[np.argmin(dists[within_radius])]
                closest_indices[i] = idx
        return closest_indices

    @staticmethod
    # Prevent extinction by cloning the fittest entities
    def prevent_extinction(entities, fittest_entities):
        entities = pygame.sprite.Group()
        for entity in fittest_entities:
            entity.hunger = 8.0 # Reset hunger
            entity.fitness = 0 # Reset fitness
            entities.add(entity)

        return entities

    # Saves game state to a file
    def save_game_state(self, filename="savegame.npz"):
        # Save data for board state
        prey_data = np.array([[prey.x, prey.y, prey.direction, prey.hunger, prey.fitness] for prey in self.preys])
        predator_data = np.array([[pred.x, pred.y, pred.direction, pred.hunger, pred.fitness] for pred in self.predators])
        prey_brains = np.array([prey.brain.get_weights() for prey in self.preys], dtype=object)
        predator_brains = np.array([pred.brain.get_weights() for pred in self.predators], dtype=object)
        # Save data for fittest agents
        fittest_preys_data = np.array([[prey.x, prey.y, prey.direction, prey.hunger, prey.fitness] for prey in self.fittest_preys])
        fittest_preys_brains = np.array([prey.brain.get_weights() for prey in self.fittest_preys], dtype=object)
        fittest_predators_data = np.array([[pred.x, pred.y, pred.direction, pred.hunger, pred.fitness] for pred in self.fittest_predators])
        fittest_predators_brains = np.array([pred.brain.get_weights() for pred in self.fittest_predators], dtype=object)
        np.savez(filename,
                prey_data=prey_data,
                predator_data=predator_data,
                prey_brains=prey_brains,
                predator_brains=predator_brains,
                food=self.food,
                fittest_preys_data=fittest_preys_data,
                fittest_preys_brains=fittest_preys_brains,
                fittest_predators_data=fittest_predators_data,
                fittest_predators_brains=fittest_predators_brains)
        self.logger.info(f"Game state saved to {filename}")

    # Loads game state from a file
    def load_game_state(self, filename="savegame.npz"):
        data = np.load(filename, allow_pickle=True)
        self.food = data['food']
        
        self.preys = pygame.sprite.Group(Prey(
            prey_data[0], # x
            prey_data[1], # y
            prey_data[2], # direction
            3.0, #speed
            0.15, #turning_rate
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), #colour
            hunger=prey_data[3], # hunger
            fitness=prey_data[4]  # fitness
            ) for prey_data in data['prey_data']
        )
        for i, prey in enumerate(self.preys):
            brain_weights = data['prey_brains'][i]
            prey.brain.set_weights(brain_weights)

        self.predators = pygame.sprite.Group(Predator(
            pred_data[0], # x
            pred_data[1], # y
            pred_data[2], # direction
            3.0, #speed
            0.15, #turning_rate
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), #colour
            hunger=pred_data[3], # hunger
            fitness=pred_data[4]  # fitness
            ) for pred_data in data['predator_data']
        )
        for i, pred in enumerate(self.predators):
            brain_weights = data['predator_brains'][i]
            pred.brain.set_weights(brain_weights)

        self.fittest_preys = np.array([Prey(
            prey_data[0], # x
            prey_data[1], # y
            prey_data[2], # direction
            3.0, #speed
            0.15, #turning_rate
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), #colour
            hunger=prey_data[3], # hunger
            fitness=prey_data[4]  # fitness
            ) for prey_data in data['fittest_preys_data']
        ], dtype=object)

        self.fittest_predators = np.array([Predator(
            pred_data[0], # x
            pred_data[1], # y
            pred_data[2], # direction
            3.0, #speed
            0.15, #turning_rate
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), #colour
            hunger=pred_data[3], # hunger
            fitness=pred_data[4]  # fitness
            ) for pred_data in data['fittest_predators_data']
        ], dtype=object)

        self.logger.info(f"Game state loaded from {filename}")

    # Creates new game state
    def start_new_simulation(self, total_starting_prey=50, total_starting_predators=50):
        #Initialize start position and attributes for the simulation
        # Generate initial food
        self.food = np.array([(random.randint(0, self.width), random.randint(0, self.height)) for i in range(100)])

        # Initialize prey
        self.preys = pygame.sprite.Group(
            Prey(
            random.randint(0, self.width), #x
            random.randint(0, self.height), #y
            random.uniform(0, math.pi), #direction 
            3.0, #speed
            0.15, #turning_rate
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)), #colour
            i+1)  # Unique ID for each prey 
            for i in range(total_starting_prey)
        )
        
        # Initialize predators
        self.predators = pygame.sprite.Group(
            Predator(
            random.randint(0, self.width), #x
            random.randint(0, self.height), #y
            random.uniform(0, math.pi), #direction
            3.0, #speed
            0.15, #turning_rate
            (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))) #colour
            for i in range(total_starting_predators)
        )

        self.fittest_preys = np.array(list(self.preys)[0:10], dtype=object)
        self.fittest_predators = np.array(list(self.predators)[0:10], dtype=object)

    # Main simulation loop
    def run(self):
        pygame.init()
    
        # Set up the display
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Predator and Prey Simulation") # Sets window title
        pygame.display.set_icon(pygame.image.load("icon.png")) # Loads icon

        # Set up simulation variables
        clock = pygame.time.Clock()
        counter = 0
        time = 0
        fps = 30
        running = True
        
        self.logger.debug("Simulation started.")
        # Main Simulation Loop
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos
                    for prey in self.preys:
                        if prey.rect.collidepoint(mouse_x, mouse_y): 
                            # Send prey's brain to renderer
                            self.brain_queue.put((prey.brain, True))
                            break
                    for pred in self.predators:
                        if pred.rect.collidepoint(mouse_x, mouse_y):
                            # Send predator's brain to renderer
                            self.brain_queue.put((pred.brain, False))
                            break

            # Fill the screen with a color
            self.screen.fill((0, 0, 0))  # Fill with black

            # Generate food
            self.food = self.generate_food(self.food, self.width, self.height)
            
            # Calculate closest food and predators for each prey using batch processing
            if self.predators and self.preys: # Both predators and preys exist
                closest_predator_indices = self.find_closest_entity_batch(np.array([[p.x, p.y] for p in self.preys]), np.array([[pred.x, pred.y] for pred in self.predators]), 200)
                closest_prey_indices = self.find_closest_entity_batch(np.array([[pred.x, pred.y] for pred in self.predators]), np.array([[p.x, p.y] for p in self.preys]), 400)
                closest_food_indices = self.find_closest_entity_batch(np.array([[p.x, p.y] for p in self.preys]), self.food, 200)
                pred_closest_food_indices = self.find_closest_entity_batch(np.array([[pred.x, pred.y] for pred in self.predators]), self.food, 200)
            elif self.preys: # No predators
                closest_food_indices = self.find_closest_entity_batch(np.array([[p.x, p.y] for p in self.preys]), self.food, 200)
                closest_predator_indices = -np.ones(len(self.preys), dtype=np.int64)
                closest_prey_indices = np.array([])
                pred_closest_food_indices = np.array([])
            elif self.predators: # No preys
                closest_predator_indices = np.array([])
                closest_prey_indices = -np.ones(len(self.predators), dtype=np.int64)
                closest_food_indices = np.array([])
                pred_closest_food_indices = self.find_closest_entity_batch(np.array([[pred.x, pred.y] for pred in self.predators]), self.food, 200)
            else: # No preys or predators
                closest_predator_indices = np.array([])
                closest_prey_indices = np.array([])
                closest_food_indices = np.array([])
                pred_closest_food_indices = np.array([])

            # Update closest food and predators for each prey
            for i, prey in enumerate(self.preys):
                if closest_food_indices[i] != -1:
                    prey.closest_food = self.food[closest_food_indices[i]]
                else:
                    prey.closest_food = None

                if closest_predator_indices[i] != -1:
                    prey.closest_predator = np.array([self.predators.sprites()[closest_predator_indices[i]].x, self.predators.sprites()[closest_predator_indices[i]].y])
                    prey.closest_predator_direction = self.predators.sprites()[closest_predator_indices[i]].direction
                else:
                    prey.closest_predator = None

            # Update closest prey for each predator
            for i, pred in enumerate(self.predators):
                if pred_closest_food_indices[i] != -1:
                    pred.closest_food = self.food[pred_closest_food_indices[i]]
                else:
                    pred.closest_food = None
                
                if closest_prey_indices[i] != -1:
                    prey_found = self.preys.sprites()[closest_prey_indices[i]]
                    pred.closest_prey = np.array([prey_found.x, prey_found.y])
                    pred.closest_prey_direction = self.preys.sprites()[closest_prey_indices[i]].direction
                else:
                    pred.closest_prey = None
                    pred.closest_prey_direction = 0.0

            # Handle eating food
            self.eat_food()
            self.eat_prey()

            # Move preys and predators
            self.preys.update()
            self.predators.update()

            clock.tick(fps)
            counter += 1
            # Handles hunger decrease and starvation every 30 frames
            if counter == fps:
                counter = 0
                time += 1
                self.preys, self.fittest_preys = self.remove_starved_entities(self.preys, self.fittest_preys)
                if len(self.preys) == 0:
                    self.preys = self.prevent_extinction(self.preys, self.fittest_preys)
                    self.logger.warning("All preys have died. Cloning the fittest preys to prevent extinction.")
                self.population_queue.put((time, len(self.preys), len(self.predators)))
            elif counter == fps // 2:
                self.predators, self.fittest_predators = self.remove_starved_entities(self.predators, self.fittest_predators)
                if len(self.predators) == 0:
                    self.predators = self.prevent_extinction(self.predators, self.fittest_predators)
                    self.logger.warning("All predators have died. Cloning the fittest predators to prevent extinction.")

            # Update the display
            self.draw_food()
            self.preys.draw(self.screen)
            self.predators.draw(self.screen)
            pygame.display.flip()

        pygame.quit()
        self.save_game_state()
        self.logger.info("Simulation ended.")
        self.brain_queue.put(("QUIT", None))
        self.population_queue.put(("QUIT", 0, 0))
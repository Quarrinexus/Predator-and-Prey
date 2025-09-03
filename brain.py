import numpy as np
import random

class Brain:
    def __init__(self, input_size, hidden_size, output_size, parent_brain=None):
        if parent_brain is None:
            self.W1 = np.random.randn(input_size, hidden_size) * 0.1
            self.b1 = np.random.randn(hidden_size)
            self.W2 = np.random.randn(hidden_size, output_size) * 0.1
            self.b2 = np.random.randn(output_size)
        else:
            mutation_strength = np.random.uniform(0, 0.3)
            self.W1 = parent_brain.W1 + np.random.randn(*parent_brain.W1.shape) * mutation_strength
            self.b1 = parent_brain.b1 + np.random.randn(*parent_brain.b1.shape) * mutation_strength
            self.W2 = parent_brain.W2 + np.random.randn(*parent_brain.W2.shape) * mutation_strength
            self.b2 = parent_brain.b2 + np.random.randn(*parent_brain.b2.shape) * mutation_strength

    def forward(self, x):
        z1 = np.dot(x, self.W1) + self.b1
        a1 = np.tanh(z1)
        z2 = np.dot(a1, self.W2) + self.b2
        return np.tanh(z2)  # Output in range -1..1

    def get_weights(self):
        return [self.W1.copy(), self.b1.copy(), self.W2.copy(), self.b2.copy()]

    def set_weights(self, weights):
        self.W1, self.b1, self.W2, self.b2 = [w.copy() for w in weights]
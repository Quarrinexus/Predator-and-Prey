import numpy as np
from numba import njit

class Brain:
    def __init__(self, input_size, first_hidden_size, second_hidden_size, output_size, parent_brain=None):
        if parent_brain is None:
            self.W1 = np.random.randn(input_size, first_hidden_size) * 0.1
            self.b1 = np.random.randn(first_hidden_size)
            self.W2 = np.random.randn(first_hidden_size, second_hidden_size) * 0.1
            self.b2 = np.random.randn(second_hidden_size)
            self.W3 = np.random.randn(second_hidden_size, output_size) * 0.1
            self.b3 = np.random.randn(output_size)
        else:
            mutation_strength = np.random.uniform(0, 0.3)
            self.W1 = parent_brain.W1 + np.random.randn(*parent_brain.W1.shape) * mutation_strength
            self.b1 = parent_brain.b1 + np.random.randn(*parent_brain.b1.shape) * mutation_strength
            self.W2 = parent_brain.W2 + np.random.randn(*parent_brain.W2.shape) * mutation_strength
            self.b2 = parent_brain.b2 + np.random.randn(*parent_brain.b2.shape) * mutation_strength
            self.W3 = parent_brain.W3 + np.random.randn(*parent_brain.W3.shape) * mutation_strength
            self.b3 = parent_brain.b3 + np.random.randn(*parent_brain.b3.shape) * mutation_strength

    @staticmethod
    @njit
    def forward(input_vector, W1, b1, W2, b2, W3, b3):
        z1 = np.dot(input_vector, W1) + b1
        a1 = np.tanh(z1)
        z2 = np.dot(a1, W2) + b2
        a2 = np.tanh(z2)
        z3 = np.dot(a2, W3) + b3
        return np.tanh(z3)  # Output in range -1..1

    def get_weights(self):
        return [self.W1.copy(), self.b1.copy(), self.W2.copy(), self.b2.copy(), self.W3.copy(), self.b3.copy()]

    def set_weights(self, weights):
        self.W1, self.b1, self.W2, self.b2, self.W3, self.b3 = [w.copy() for w in weights]
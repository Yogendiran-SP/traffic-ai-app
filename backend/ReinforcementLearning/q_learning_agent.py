import random
from collections import defaultdict

class QLearningAgent:
    def __init__(self, actions, alpha=0.1, gamma=0.9, epsilon=0.2):
        self.q_table = defaultdict(lambda: [0.0 for _ in actions])
        self.actions = actions
        self.alpha = alpha      # Learning rate
        self.gamma = gamma      # Discount factor
        self.epsilon = epsilon  # Exploration rate

    def choose_action(self, state):
        """Epsilon-greedy action selection"""
        if random.random() < self.epsilon:
            return random.choice(self.actions)  # Explore
        else:
            q_values = self.q_table[state]
            return self.argmax(q_values)        # Exploit

    def learn(self, state, action, reward, next_state):
        current_q = self.q_table[state][action]
        max_next_q = max(self.q_table[next_state])
        new_q = current_q + self.alpha * (reward + self.gamma * max_next_q - current_q)
        self.q_table[state][action] = new_q

    def argmax(self, values):
        """Return the index of the highest value"""
        max_val = max(values)
        max_indices = [i for i, v in enumerate(values) if v == max_val]
        return random.choice(max_indices)

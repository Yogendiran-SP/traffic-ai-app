import numpy as np
import random
import joblib
from trafficenv import TrafficEnv

# Hyperparameters
alpha = 0.1       # Learning rate
gamma = 0.9       # Discount factor
epsilon = 0.1     # Exploration rate
episodes = 1000

# Initialize environment
env = TrafficEnv()

# Initialize Q-table with zeros
# States = 10000 possible traffic combinations (10 per road)
# Actions = 4 roads to choose (0 to 3)
Q_table = np.zeros((20000, 4))

# Training loop
for episode in range(episodes):
    state = env.reset()
    done = False
    total_reward = 0

    while not done:
        if random.uniform(0, 1) < epsilon:
            action = env.action_space_sample()  # Explore
        else:
            action = np.argmax(Q_table[state])  # Exploit

        next_state, reward, done = env.step(action)

        # Q-learning update
        Q_table[state][action] += alpha * (reward + gamma * np.max(Q_table[next_state]) - Q_table[state][action])

        state = next_state
        total_reward += reward

    if (episode + 1) % 100 == 0:
        print(f"Episode {episode+1}/{episodes}, Total Reward: {total_reward:.2f}")

# Save the trained Q-table
joblib.dump(Q_table, "../rl_model/q_table.pkl")
print("Q-table training completed and saved.")
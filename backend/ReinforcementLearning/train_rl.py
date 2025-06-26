import pandas as pd
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

# Load data
df = pd.read_csv("../traffic_log.csv")

# Feature Engineering
df["timestamp"] = pd.to_datetime(df["timestamp"])

# Input features
X = df[['north', 'east', 'south', 'west', 'green_road']]

y = df[['duration']] # Green duration

# Train/Test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Model creation - Random Forest Regression
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model
with open("../rl_model/rl_duration_predictor.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ RL Duration Predictor Model trained and saved!")
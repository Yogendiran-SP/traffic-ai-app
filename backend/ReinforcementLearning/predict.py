import joblib
import pandas as pd

model = joblib.load("../rl_model/rl_duration_predictor.pkl")  # Load your trained RL model

def predict_duration(road_counts, green_road):
    data = {
        'north': road_counts.get('north', 0),
        'east': road_counts.get('east', 0),
        'south': road_counts.get('south', 0),
        'west': road_counts.get('west', 0),
        'green_road': green_road
    }
    df = pd.DataFrame([data])
    return int(model.predict(df)[0])  # Return predicted duration

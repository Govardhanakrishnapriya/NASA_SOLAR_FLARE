import gradio as gr
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import os

# Check if models exist, if not train them
def train_models():
    print("Training models...")
    
    # Create sample solar flare data (replace with your actual data)
    np.random.seed(42)
    n_samples = 2000
    
    # Generate synthetic data
    data = {
        'active_region': np.random.randint(10000, 15000, n_samples),
        'linked_events': np.random.choice([0, 1], n_samples),
        'duration': np.random.uniform(5, 120, n_samples),
        'rise_time': np.random.uniform(2, 60, n_samples),
        'month': np.random.randint(1, 13, n_samples),
        'hour': np.random.randint(0, 24, n_samples),
        'flare_class': np.random.choice(['A', 'B', 'C', 'M', 'X'], n_samples, 
                                       p=[0.1, 0.3, 0.35, 0.2, 0.05])
    }
    
    df = pd.DataFrame(data)
    
    # Prepare features
    feature_cols = ['active_region', 'linked_events', 'duration', 'rise_time', 'month', 'hour']
    X = df[feature_cols].values
    y = df['flare_class'].values
    
    # Encode labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Random Forest
    rf = RandomForestClassifier(n_estimators=100, random_state=42)
    rf.fit(X_scaled, y_encoded)
    
    # Train MLP
    mlp = MLPClassifier(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42)
    mlp.fit(X_scaled, y_encoded)
    
    # Save models
    with open("solar_flare_rf.pkl", "wb") as f:
        pickle.dump(rf, f)
    
    with open("solar_flare_mlp.pkl", "wb") as f:
        pickle.dump(mlp, f)
    
    with open("solar_flare_scaler.pkl", "wb") as f:
        pickle.dump(scaler, f)
    
    with open("solar_flare_encoder.pkl", "wb") as f:
        pickle.dump(le, f)
    
    print("Models trained and saved!")
    return rf, mlp, scaler, le

# Load or train models
try:
    print("Loading existing models...")
    with open("solar_flare_rf.pkl", "rb") as f:
        rf = pickle.load(f)
    
    with open("solar_flare_mlp.pkl", "rb") as f:
        mlp = pickle.load(f)
    
    with open("solar_flare_scaler.pkl", "rb") as f:
        scaler = pickle.load(f)
    
    with open("solar_flare_encoder.pkl", "rb") as f:
        le = pickle.load(f)
    print("Models loaded successfully!")
except FileNotFoundError:
    print("Models not found. Training new models...")
    rf, mlp, scaler, le = train_models()

def predict_flare(
    active_region,
    linked_events,
    duration,
    rise_time,
    month,
    hour,
    model_choice
):
    # Prepare input
    X = np.array([[
        active_region,
        linked_events,
        duration,
        rise_time,
        month,
        hour
    ]])
    
    # Scale input
    X_scaled = scaler.transform(X)
    
    # Predict based on model choice
    if model_choice == "Random Forest":
        probabilities = rf.predict_proba(X_scaled)[0]
    else:  # MLP Neural Network
        probabilities = mlp.predict_proba(X_scaled)[0]
    
    predicted_index = np.argmax(probabilities)
    predicted_class = le.inverse_transform([predicted_index])[0]
    confidence = probabilities[predicted_index] * 100
    
    # Format result
    result = f"""
# ☀️ Solar Flare Prediction

### Predicted Flare Class
**{predicted_class}**

### Confidence
**{confidence:.2f}%**

### Class Probabilities
"""
    
    for cls, prob in zip(le.classes_, probabilities):
        result += f"\n- {cls}: {prob*100:.2f}%"
    
    return result

# Create Gradio interface
with gr.Blocks(title="NASA Solar Flare Predictor") as app:
    
    gr.Markdown("""
    # ☀️ NASA Solar Flare Predictor
    
    Predict Solar Flare Class using Machine Learning and Neural Networks.
    """)
    
    with gr.Row():
        with gr.Column():
            active_region = gr.Number(
                label="Active Region Number",
                value=12000
            )
            
            linked_events = gr.Dropdown(
                choices=[0, 1],
                value=0,
                label="Linked Events (0=No, 1=Yes)"
            )
            
            duration = gr.Number(
                label="Duration (Minutes)",
                value=10
            )
            
            rise_time = gr.Number(
                label="Rise Time (Minutes)",
                value=5
            )
            
            month = gr.Slider(
                minimum=1,
                maximum=12,
                value=6,
                step=1,
                label="Month"
            )
            
            hour = gr.Slider(
                minimum=0,
                maximum=23,
                value=12,
                step=1,
                label="Hour (UTC)"
            )
            
            model_choice = gr.Radio(
                choices=[
                    "Random Forest",
                    "MLP Neural Network"
                ],
                value="Random Forest",
                label="Select Model"
            )
            
            predict_btn = gr.Button(
                "Predict Solar Flare",
                variant="primary"
            )
        
        with gr.Column():
            output = gr.Markdown()
    
    predict_btn.click(
        fn=predict_flare,
        inputs=[
            active_region,
            linked_events,
            duration,
            rise_time,
            month,
            hour,
            model_choice
        ],
        outputs=output
    )

if __name__ == "__main__":
    app.launch()
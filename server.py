from flask import Flask, request, jsonify, render_template
import pickle
import json
import numpy as np
import os
from openai import OpenAI

app = Flask(__name__)

# -------------------------------
# Load model
# -------------------------------
with open('banglore_home_prices_model.pickle', 'rb') as f:
    model = pickle.load(f)

# Load columns
with open("columns.json", "r") as f:
    data_columns = json.load(f)['data_columns']

# -------------------------------
# Grok client
# -------------------------------
client = OpenAI(
    api_key=os.getenv("XAI_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# -------------------------------
# Prediction function
# -------------------------------
def predict_price(location, sqft, bath, bhk):
    try:
        loc_index = data_columns.index(location)
    except:
        loc_index = -1

    x = np.zeros(len(data_columns))
    x[0] = sqft
    x[1] = bath
    x[2] = bhk

    if loc_index >= 0:
        x[loc_index] = 1

    return round(model.predict([x])[0], 2)


# -------------------------------
# Explanation function (SAFE)
# -------------------------------
def generate_explanation(location, sqft, bath, bhk, price):
    prompt = f"""
    Explain why a house in {location} with {bhk} BHK, {bath} bathrooms,
    and {sqft} sqft costs around {price} lakhs.
    Keep it simple and under 4 lines.
    """

    try:
        response = client.chat.completions.create(
            model="grok-1.5",   # 🔥 updated model
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("LLM ERROR:", e)

        # ✅ fallback explanation (IMPORTANT)
        return f"Price depends on location ({location}), size ({sqft} sqft), number of rooms ({bhk} BHK), and bathrooms ({bath})."


# -------------------------------
# Routes
# -------------------------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/locations')
def get_locations():
    return jsonify({
        'locations': data_columns[3:]
    })


@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    location = data['location']
    sqft = float(data['sqft'])
    bath = int(data['bath'])
    bhk = int(data['bhk'])

    price = predict_price(location, sqft, bath, bhk)

    # 🔥 Always returns something
    explanation = generate_explanation(location, sqft, bath, bhk, price)

    return jsonify({
        'predicted_price': price,
        'explanation': explanation
    })


# -------------------------------
# Run server
# -------------------------------
if __name__ == "__main__":
import os
port = int(os.environ.get("PORT", 10000))
app.run(host="0.0.0.0", port=port)
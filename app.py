import numpy as np
from flask import Flask, request, render_template
import pickle

# Create an app object
app = Flask(__name__)

# load the train model and scalers
model = pickle.load(open("models/model.pkl", "rb"))
fa = pickle.load(open("models/factoranalysis_parameters.pkl", "rb"))
scaler = pickle.load(open("models/scaler.pkl", "rb"))


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    input_data = [float(x) for x in request.form.values()]
    print(input_data) #KEEP FROM HERE CHECK THE LAST TWO VALUES
    
    refactored_data = fa.transform(np.array(input_data).reshape(1,-1))
    scaled_data = scaler.transform(np.array(refactored_data))
    prediction = model.predict(scaled_data)[0]
    
    probabilities = model.predict_proba(scaled_data)
    class_probability = round(max(probabilities[0]), 2)
    
    prediction = "MORE" if prediction == 1 else "LESS"
    
    prediction_text = "I predict that" + prediction + " than 4.5 yellow cards will be booked in this football match with a probability "+ str(class_probability) +". The fair betting odds should be " + str(round(1/class_probability, 1))
    print(prediction_text)
    return render_template("index.html", prediction_text = prediction_text)


if __name__ == "__main__":
    app.run()
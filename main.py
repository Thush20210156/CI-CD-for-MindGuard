import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

Value = ""
# Load the sentiment analysis model
with open('LRPWeights.pkl', 'rb') as file:
    sentiment_model = pickle.load(file)
with open('TFIDFWeights.pkl', 'rb') as file:
    tfidf = pickle.load(file)

# Create feature vectors
def preprocess_data(sentence):
    X = tfidf.transform([sentence])
    return X

# Define the depression screening function
def screen_for_depression(responses):
    
    # Use the sentiment analysis model to classify responses
    responses = responses.split(',')
    sentences = [response for response in responses]
    
    score = []
    for sentence in sentences:
        sentence = sentence.strip()
        x = preprocess_data(sentence)
        prediction = sentiment_model.predict(x)[0]
        score.append(prediction)

    # Calculate total score and assign depression level
    total_score = sum(score)

    if total_score in range(0, 10):
        depression_level = 'Severe'
        interpretation = "Your responses suggest that you may be experiencing severe symptoms of depression. It's crucial that you seek help from a mental health professional as soon as possible. In case of an emergency, please call 911 or your local emergency number."

    elif total_score in range(10, 13):
        depression_level = 'Moderate'
        interpretation = "Your responses suggest that you may be experiencing moderate symptoms of depression. It's important to seek help from a mental health professional to manage your symptoms."
    
    elif total_score in range(13, 18):
        depression_level = 'Mild'
        interpretation = "Your responses suggest that you may be experiencing mild symptoms of depression. It's important to take care of yourself and seek help if your symptoms worsen."
    
    else:
        depression_level = 'Normal'
        interpretation = "Your responses suggest that you do not have any symptoms of depression. However, it is recommended to take care of yourself."
        
    # Generate report
    report = {
        "Name": request.json.get('name'),
        "Sentiment Scores": int(total_score),
        "Total Sentiment Score": int(total_score),
        "Depression Level": depression_level,
        "Interpretation": interpretation,
        "Urgent": "No"
    }

    # Prompt emergency numbers if depression is severe
    if depression_level == "Severe":
        report['Urgent'] = "Please call emergency services (911 or your local emergency number) for immediate help."

    return report


# Define endpoint for depression screening
@app.route('/screen_for_depression', methods=['POST'])
def depression_screening():
    global Value
    
    # Get user responses from the request body
    responses = request.json.get('responses')

    # Call the screening function and return the report
    report = screen_for_depression(responses)
    Value = report

    json_response = jsonify(report)
    
    return json_response

# Define endpoint for post-value retrival
@app.route('/result', methods=['GET'])
def get_value():

    # Return the previous report
    json_response = jsonify(Value)

    return json_response

if __name__ == '__main__':
    app.run(debug=True)

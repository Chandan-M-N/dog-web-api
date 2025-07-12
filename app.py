from flask import Flask, render_template, jsonify
from models.db import get_all_dogs
from collections import defaultdict


app = Flask(__name__)

# Webpage Endpoint
@app.route('/')
def home():
    return render_template('index.html')

@app.route("/dogs", methods=['GET'])
def list_dogs():
    """
    GET endpoint to fetch all dogs
    Returns: JSON response with dog list or error
    """
    try:
        dogs = get_all_dogs()
        breeds_dict = defaultdict(list)
        for dog in dogs:
            if dog['sub_breed']:
                breeds_dict[dog['breed']].append(dog['sub_breed'].capitalize())
            else:
                breeds_dict[dog['breed'].capitalize()] = [] 
        
        # Convert to regular dict and sort
        breeds_dict = dict(sorted(breeds_dict.items()))
        main_breeds = list(breeds_dict.keys())
        print(breeds_dict,main_breeds)
        return render_template(
            'dogs.html',
            breeds_dict=breeds_dict,
            main_breeds=main_breeds
        )
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100,debug=True)
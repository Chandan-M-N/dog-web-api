from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from models.db import get_all_dogs, add_dog, delete_dog, add_sub_breed
from collections import defaultdict


app = Flask(__name__)
app.secret_key = 'dogwebapi'

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


@app.route('/add-dog', methods=['POST'])
def add_dog_route():
    """
    Add a new dog breed or sub-breed
    Accepts: breed (required), sub_breed (optional)
    Redirects: back to /dogs with success/error message
    """
    try:
        breed = request.form.get('breed', '').strip().lower()
        sub_breed = request.form.get('sub_breed', '').strip().lower() or None
        
        if not breed:
            flash('Breed is required', 'error')
            return redirect(url_for('list_dogs'))
        print(breed,"add")
        success = add_dog(breed, sub_breed)
        
        if success:
            flash_message = f"New Breed '{breed}' and Sub-breed '{sub_breed}' added!" if sub_breed else f"Breed '{breed}' added"
            flash(flash_message, 'success')
        else:
            flash_message = f"Breed '{breed}' already exists" if not sub_breed else f"Combination '{breed} - {sub_breed}' already exists"
            flash(flash_message, 'error')
            
        return redirect(url_for('list_dogs'))
        
    except Exception as e:
        flash(f'Error adding dog: {str(e)}', 'error')
        print(f'Error adding dog: {str(e)}', 'error')
        return redirect(url_for('list_dogs'))
    
@app.route('/add-subbreed', methods=['POST'])
def add_subbreed_route():
    """
    Add a new sub-breed to an existing breed
    Accepts: breed (required), sub_breed (required)
    Redirects: back to /dogs with success/error message
    """
    try:
        breed = request.form.get('breed', '').strip().lower()
        sub_breed = request.form.get('sub_breed', '').strip().lower()
        
        if not breed or not sub_breed:
            flash('Both breed and sub-breed are required', 'error')
            return redirect(url_for('list_dogs'))
        
        success = add_sub_breed(breed, sub_breed)
        
        if success:
            flash(f"Sub-breed '{sub_breed}' successfully added to '{breed}'", 'success')
        else:
            flash(f"Sub-breed '{sub_breed}' already exists for '{breed}'", 'error')
            
        return redirect(url_for('list_dogs'))
        
    except Exception as e:
        flash(f'Error adding sub-breed: {str(e)}', 'error')
        return redirect(url_for('list_dogs'))

@app.route('/delete-breed', methods=['POST'])
def delete_breed_route():
    """
    Delete all occurrences of a breed (including sub-breeds)
    Accepts: breed (required)
    Redirects: back to /dogs with success/error message
    """
    try:
        breed = request.form.get('breed', '').strip().lower()
        
        if not breed:
            flash('Breed is required', 'error')
            return redirect(url_for('list_dogs'))
        
        success = delete_dog(breed)  # sub_breed=None by default
        
        if success:
            flash(f"Breed '{breed}' and all its sub-breeds deleted", 'success')
        else:
            flash(f"Breed '{breed}' not found", 'error')
            
        return redirect(url_for('list_dogs'))
        
    except Exception as e:
        flash(f'Error deleting breed: {str(e)}', 'error')
        return redirect(url_for('list_dogs'))

@app.route('/delete-subbreed', methods=['POST'])
def delete_subbreed_route():
    """
    Delete a specific breed/sub-breed combination
    Accepts: breed (required), sub_breed (required)
    Redirects: back to /dogs with success/error message
    """
    try:
        breed = request.form.get('breed', '').strip().lower()
        sub_breed = request.form.get('sub_breed', '').strip().lower()

        print(breed,sub_breed,"delete-subbreed")
        
        if not breed or not sub_breed:
            flash('Both breed and sub-breed are required', 'error')
            return redirect(url_for('list_dogs'))
        
        success = delete_dog(breed, sub_breed)
        
        if success:
            flash(f"Sub-breed '{sub_breed}' deleted from '{breed}'", 'success')
        else:
            flash(f"Combination '{breed} - {sub_breed}' not found", 'error')
            
        return redirect(url_for('list_dogs'))
        
    except Exception as e:
        flash(f'Error deleting sub-breed: {str(e)}', 'error')
        return redirect(url_for('list_dogs'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100,debug=True)
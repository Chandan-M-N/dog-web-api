from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from models.db import get_all_dogs, add_dog, delete_dog, add_sub_breed, edit_dog
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
                breeds_dict[dog['breed'].capitalize()].append(dog['sub_breed'].capitalize())
            else:
                breeds_dict[dog['breed'].capitalize()] = [] 
        # Convert to regular dict and sort
        breeds_dict = dict(sorted(breeds_dict.items()))
        main_breeds = list(breeds_dict.keys())
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


@app.route('/edit-dog', methods=['POST'])
def edit_dog_route():
    """
    Handle breed and sub-breed edits from the form
    Accepts: 
    - original_breed (required)
    - breed (new breed name)
    - original_sub_breeds[] (array)
    - sub_breeds[] (array)
    Redirects: back to /dogs with success/error message
    """
    try:
        original_breed = request.form.get('original_breed', '').strip().lower()
        new_breed = request.form.get('breed', '').strip().lower()
        
        if not original_breed or not new_breed:
            flash('Breed name is required', 'error')
            return redirect(url_for('list_dogs'))

        # # Get sub-breed arrays from form
        original_sub_breeds = request.form.getlist('original_sub_breeds')
        new_sub_breeds = request.form.getlist('sub_breeds')

        # Validate we have matching counts
        if len(original_sub_breeds) != len(new_sub_breeds):
            flash('Sub-breed data mismatch', 'error')
            return redirect(url_for('list_dogs'))

        # Handle main breed update (if breed name changed)
        if original_breed != new_breed:
            success = edit_dog(
                original_breed=original_breed,
                new_breed=new_breed,
                original_sub_breed=None,
                new_sub_breed=None
            )
            if not success:
                flash(f"Breed '{new_breed}' already exists", 'error')
                return redirect(url_for('list_dogs'))

        # Handle sub-breed updates
        for original_sub, new_sub in zip(original_sub_breeds, new_sub_breeds):
            original_sub = original_sub.strip().lower() or None
            new_sub = new_sub.strip().lower() or None
            
            if original_sub != new_sub:
                success = edit_dog(
                    original_breed=new_breed,  # Use potentially updated breed name
                    new_breed=new_breed,
                    original_sub_breed=original_sub,
                    new_sub_breed=new_sub
                )
                if not success:
                    flash(f"Sub-breed combination '{new_breed} - {new_sub}' already exists", 'error')
                    return redirect(url_for('list_dogs'))

        flash(f"Successfully updated Breed '{original_breed}'", 'success')
        return redirect(url_for('list_dogs'))
        
    except Exception as e:
        flash(f'Error updating dog: {str(e)}', 'error')
        return redirect(url_for('list_dogs'))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100)
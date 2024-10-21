from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import connect_db, db, User, FavoriteDrink
from forms import RegisterUserForm, LoginForm, IngredientSearchForm, EditProfileForm, ChangePasswordForm, DeleteAccountForm
import requests
from flask_wtf.csrf import CSRFProtect

app = Flask(__name__)

# Configuration settings for the app
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///whatsyourpoison'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "Sharapova1"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False  

# Enable debugging toolbar
toolbar = DebugToolbarExtension(app)

# Set up Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"

# Enable CSRF protection
csrf = CSRFProtect()
csrf.init_app(app)

# Connect to the database and create tables if they don't exist
with app.app_context():
    connect_db(app)
    db.create_all()

# Load user by ID for authentication
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Route for the home page (registration page)
@app.route('/', methods=['GET', 'POST'])
def index():
    form = RegisterUserForm()
    if form.validate_on_submit():
        # Check if the phone number or email already exists
        if User.is_phone_number_email_duplicate(form.phone_number.data, form.email.data):
            flash('Phone number or email already exists. Please use different ones.', 'danger')
            return redirect(url_for('index'))

        # Create new user instance
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            dob=form.dob.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip=form.zip.data,
            phone_number=form.phone_number.data,
            email=form.email.data,
        )
        
        # Hash the password and save the user
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created successfully!', 'success')
        return redirect(url_for('login'))

    return render_template('index.html', form=form)

# Route to edit the user's profile
@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(obj=current_user)  # Prefill form with current user's data

    if form.validate_on_submit():
        print("Form submitted and validated!")  # Debugging log
        # Update user information with new values from the form
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.dob = form.dob.data
        current_user.address = form.address.data
        current_user.city = form.city.data
        current_user.state = form.state.data
        current_user.zip = form.zip.data
        current_user.phone_number = form.phone_number.data
        current_user.email = form.email.data
        
        db.session.commit()
        flash('Your profile has been updated successfully!', 'success')
        return redirect(url_for('profile'))

    # Log form errors if validation fails
    print("Form not submitted or did not validate. Errors:", form.errors)  # Debugging log
    return render_template('edit_profile.html', form=form)

# Route to delete the user account
@app.route('/delete-account', methods=['GET', 'POST'])
@login_required
def delete_account():
    form = DeleteAccountForm()

    if form.validate_on_submit():
        # Check if the provided password matches the current user's password
        if not current_user.check_password(form.password.data):
            flash('Incorrect password. Please try again.', 'danger')
            return redirect(url_for('delete_account'))

        # Delete the user account from the database
        db.session.delete(current_user)
        db.session.commit()

        flash('Your account has been deleted successfully.', 'success')
        return redirect(url_for('index'))  # Redirect to homepage or sign-up page

    return render_template('delete_account.html', form=form)

# Route for logging in users
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # Check if the user exists
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            # Verify the password
            if user.check_password(form.password.data):
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('profile'))
            else:
                flash('Incorrect password. Please try again.', 'danger')
        else:
            # User not found, prompt to register
            flash('No account found with that email. Please register an account.', 'warning')
            return redirect(url_for('index'))  # Redirect to registration page

    return render_template('login.html', form=form)

# Route to change the password
@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        # Verify current password
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect.', 'danger')
            return redirect(url_for('change_password'))

        # Update with the new password
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash('Your password has been updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('change_password.html', form=form)

# Route to log out the user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# Route for displaying the user's profile
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

# Route for drink search page
@app.route('/drink-search')
@login_required  
def drink_search():
    return render_template('drink_search.html')

# Route for handling drink search results
@app.route('/search-drink-results', methods=['GET'])
@login_required
def search_drink_results():
    drink_name = request.args.get('drink_name')
    
    if not drink_name:
        flash('Please enter a drink name to search.', 'warning')
        return redirect(url_for('drink_search'))

    # Call external API to search for drinks
    api_url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={drink_name}"
    response = requests.get(api_url)
    data = response.json()

    if data and data.get('drinks'):
        return render_template('search_drink_results.html', drinks=data['drinks'])
    else:
        flash('No drinks found. Try searching for something else!', 'danger')
        return redirect(url_for('drink_search'))

# Route to fetch cocktails by the first letter
@app.route('/cocktails-by-letter/<letter>', methods=['GET'])
@login_required
def cocktails_by_letter(letter):
    # Ensure the letter is a single character
    if len(letter) != 1 or not letter.isalpha():
        flash("Please provide a single valid letter.", "danger")
        return redirect(url_for('index'))
    
    # Call the external API to fetch cocktails by the first letter
    api_url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?f={letter}"
    response = requests.get(api_url)
    data = response.json()

    # Check if the API returned any drinks
    if data and data.get('drinks'):
        return render_template('cocktails_by_letter.html', drinks=data['drinks'], letter=letter)
    else:
        flash("No cocktails found starting with that letter.", "warning")
        return redirect(url_for('cocktails_by_letter'))

# Route to filter cocktails by type (Alcoholic/Non-Alcoholic)
@app.route('/filter-by-alcoholic/<type>', methods=['GET'])
@login_required
def filter_by_alcoholic(type):
    if type not in ['Alcoholic', 'Non_Alcoholic']:
        flash('Invalid filter type. Please choose "Alcoholic" or "Non_Alcoholic".', 'danger')
        return redirect(url_for('index'))
    
    api_url = f"https://www.thecocktaildb.com/api/json/v1/1/filter.php?a={type}"
    response = requests.get(api_url)
    data = response.json()

    if data and data.get('drinks'):
        return render_template('filter_by_alcoholic.html', drinks=data['drinks'], type=type)
    else:
        flash(f'No {type.lower()} drinks found.', 'warning')
        return redirect(url_for('index'))

# Route to add a drink to favorites
@app.route('/add-favorite/<drink_id>', methods=['POST'])
@login_required
def add_favorite(drink_id):
    drink_name = request.form.get('drink_name')
    drink_thumb = request.form.get('drink_thumb')

    # Check if this drink is already a favorite for the user
    existing_favorite = FavoriteDrink.query.filter_by(user_id=current_user.id, drink_id=drink_id).first()
    if existing_favorite:
        return jsonify({'success': False, 'message': 'This drink is already in your favorites!'})

    # Create a new favorite entry
    new_favorite = FavoriteDrink(user_id=current_user.id, drink_name=drink_name, drink_id=drink_id, drink_thumb=drink_thumb)
    db.session.add(new_favorite)
    db.session.commit()

    return jsonify({'success': True})

# Route to display user's favorite drinks
@app.route('/favorites')
@login_required
def favorites():
    favorites = FavoriteDrink.query.filter_by(user_id=current_user.id).all()
    return render_template('favorites.html', favorites=favorites)

# Route to remove a favorite drink
@app.route('/remove-favorite/<int:favorite_id>', methods=['POST'])
@login_required
def remove_favorite(favorite_id):
    favorite = FavoriteDrink.query.get_or_404(favorite_id)

    # Ensure the current user owns this favorite
    if favorite.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'You do not have permission to remove this favorite.'})

    # Remove the favorite from the database
    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'success': True, 'favorite_id': favorite_id})

# Route to fetch a random cocktail
@app.route('/random-cocktail', methods=['GET'])
@login_required
def random_cocktail():
    response = requests.get('https://www.thecocktaildb.com/api/json/v1/1/random.php')
    
    if response.status_code == 200:
        data = response.json()
        drink = data['drinks'][0] if data['drinks'] else None
        return render_template('random_cocktail.html', drink=drink)
    else:
        return jsonify({"error": "Failed to retrieve random cocktail."}), 500

# Route to search for cocktails by ingredient
@app.route('/ingredient-search', methods=['GET', 'POST'])
@login_required
def ingredient_search():
    form = IngredientSearchForm()
    if form.validate_on_submit():
        ingredient_name = form.ingredient_name.data
        
        if not ingredient_name:
            flash('Please enter an ingredient name to search.', 'warning')
            return redirect(url_for('ingredient_search'))
        
        api_url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?i={ingredient_name}"
        response = requests.get(api_url)
        data = response.json()

        if data and data.get('ingredients'):
            return render_template('ingredient_details.html', ingredients=data['ingredients'])
        else:
            flash('No ingredients found. Try searching for something else!', 'danger')
            return redirect(url_for('ingredient_search'))

    return render_template('ingredient_search.html', form=form)

# Run the app
if __name__ == "__main__":
    app.run(debug=True)


        



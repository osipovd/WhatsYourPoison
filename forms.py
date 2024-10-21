from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from choices import STATE_CHOICES  

class RegisterUserForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=30)])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(max=50)])
    city = StringField('City', validators=[DataRequired(), Length(max=30)])
    state = SelectField('State', choices=STATE_CHOICES, validators=[DataRequired()])
    zip = StringField('ZIP Code', validators=[DataRequired(), Length(min=5, max=5)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=40)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=130)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Sign Up')

class EditProfileForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=30)])
    dob = DateField('Date of Birth', format='%Y-%m-%d', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(max=50)])
    city = StringField('City', validators=[DataRequired(), Length(max=30)])
    state = SelectField('State', choices=STATE_CHOICES, validators=[DataRequired()])
    zip = StringField('ZIP Code', validators=[DataRequired(), Length(min=5, max=5)])
    phone_number = StringField('Phone Number', validators=[DataRequired(), Length(max=15)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=40)])
    submit = SubmitField('Update Profile')
    
class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=6, max=130)])
    confirm_new_password = PasswordField(
        'Confirm New Password',
        validators=[DataRequired(), EqualTo('new_password', message='Passwords must match')]
    )
    submit = SubmitField('Change Password')

class DeleteAccountForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Delete Account')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')
    
class IngredientSearchForm(FlaskForm):
    ingredient_name = StringField('Ingredient Name')
    submit = SubmitField('Search')

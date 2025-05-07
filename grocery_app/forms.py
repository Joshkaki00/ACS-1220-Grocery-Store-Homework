from flask_wtf import FlaskForm
from wtforms import (
    StringField, SelectField, SubmitField, FloatField,
    PasswordField, IntegerField, URLField
)
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import (
    DataRequired, Length, URL, NumberRange, ValidationError, Optional, EqualTo
)
from grocery_app.models import GroceryStore, GroceryItem, ItemCategory, User


class GroceryStoreForm(FlaskForm):
    """Form for adding/updating a GroceryStore."""
    title = StringField(
        'Title',
        validators=[DataRequired(), Length(min=1, max=80)]
    )
    address = StringField(
        'Address',
        validators=[DataRequired(), Length(min=1, max=200)]
    )
    submit = SubmitField('Submit')


class GroceryItemForm(FlaskForm):
    """Form for adding/updating a GroceryItem."""
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(min=1, max=80)]
    )
    price = FloatField(
        'Price',
        validators=[
            DataRequired(),
            NumberRange(min=0, message='Price must be greater than 0')
        ]
    )
    category = SelectField(
        'Category',
        choices=[(category.value, category.value) for category in ItemCategory]
    )
    photo_url = URLField(
        'Photo URL',
        validators=[Optional(), URL()]
    )
    store = QuerySelectField(
        'Store',
        query_factory=lambda: GroceryStore.query,
        allow_blank=False
    )
    submit = SubmitField('Submit')


class ShoppingListForm(FlaskForm):
    """Form for adding/updating a ShoppingList."""
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(min=1, max=80)]
    )
    submit = SubmitField('Submit')


class ShoppingListItemForm(FlaskForm):
    """Form for adding/updating a ShoppingListItem."""
    item = QuerySelectField(
        'Item',
        query_factory=lambda: GroceryItem.query,
        allow_blank=False
    )
    quantity = IntegerField(
        'Quantity',
        validators=[
            DataRequired(),
            NumberRange(min=1, message='Quantity must be at least 1')
        ]
    )
    submit = SubmitField('Submit')


class SignUpForm(FlaskForm):
    """Form for adding users."""
    username = StringField(
        'Username',
        validators=[DataRequired(), Length(min=3, max=80)]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6)]
    )
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match')
        ]
    )
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError(
                'Username already taken. Please pick another.'
            )


class LoginForm(FlaskForm):
    """Form for logging in."""
    username = StringField(
        'Username',
        validators=[DataRequired()]
    )
    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )
    submit = SubmitField('Log In')

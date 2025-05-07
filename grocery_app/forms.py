from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, FloatField
from wtforms_sqlalchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Length, URL
from grocery_app.models import GroceryStore, ItemCategory


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
    price = FloatField('Price', validators=[DataRequired()])
    category = SelectField(
        'Category',
        choices=[(category.value, category.value) for category in ItemCategory]
    )
    photo_url = StringField('Photo URL', validators=[URL()])
    store = QuerySelectField(
        'Store',
        query_factory=lambda: GroceryStore.query,
        allow_blank=False
    )
    submit = SubmitField('Submit')

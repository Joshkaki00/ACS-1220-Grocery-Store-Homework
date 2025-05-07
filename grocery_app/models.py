from grocery_app.extensions import db
from flask_login import UserMixin
import enum
from datetime import datetime


class ItemCategory(enum.Enum):
    """Categories of grocery items."""
    PRODUCE = 'Produce'
    DELI = 'Deli'
    BAKERY = 'Bakery'
    PANTRY = 'Pantry'
    FROZEN = 'Frozen'
    OTHER = 'Other'

    @classmethod
    def _missing_(cls, value):
        """Handle case-insensitive enum values."""
        for member in cls:
            if member.value.lower() == value.lower():
                return member
        return None


# Association table for many-to-many relationship between GroceryItem and ShoppingList
shopping_list_items = db.Table(
    'shopping_list_items',
    db.Column(
        'shopping_list_id',
        db.Integer,
        db.ForeignKey('shopping_list.id'),
        primary_key=True
    ),
    db.Column(
        'item_id',
        db.Integer,
        db.ForeignKey('grocery_item.id'),
        primary_key=True
    ),
    db.Column('quantity', db.Integer, default=1)
)


class GroceryStore(db.Model):
    """Grocery Store model."""
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    items = db.relationship('GroceryItem', back_populates='store')


class GroceryItem(db.Model):
    """Grocery Item model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float(precision=2), nullable=False)
    category = db.Column(
        db.Enum(
            ItemCategory,
            values_callable=lambda x: [e.value for e in ItemCategory]
        ),
        default=ItemCategory.OTHER
    )
    photo_url = db.Column(db.String)
    store_id = db.Column(
        db.Integer, db.ForeignKey('grocery_store.id'), nullable=False)
    store = db.relationship('GroceryStore', back_populates='items')
    shopping_lists = db.relationship(
        'ShoppingList',
        secondary=shopping_list_items,
        back_populates='items'
    )


class ShoppingList(db.Model):
    """Shopping List model."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='shopping_lists')
    items = db.relationship(
        'GroceryItem',
        secondary=shopping_list_items,
        back_populates='shopping_lists'
    )

    def get_item_quantity(self, item_id):
        """Get the quantity of an item in the shopping list."""
        result = db.session.query(shopping_list_items).filter_by(
            shopping_list_id=self.id,
            item_id=item_id
        ).first()
        return result.quantity if result else 0

    @property
    def total_price(self):
        """Calculate the total price of all items in the shopping list."""
        total = 0
        for item in self.items:
            quantity = self.get_item_quantity(item.id)
            total += item.price * quantity
        return total


class User(UserMixin, db.Model):
    """User model."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    shopping_lists = db.relationship('ShoppingList', back_populates='user')

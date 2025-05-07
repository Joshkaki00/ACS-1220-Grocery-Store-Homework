from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from grocery_app.models import (
    GroceryStore, GroceryItem, ShoppingList, User, shopping_list_items
)
from grocery_app.forms import (
    GroceryStoreForm, GroceryItemForm, ShoppingListForm,
    ShoppingListItemForm, SignUpForm, LoginForm
)
from grocery_app.extensions import db, bcrypt

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__)

##########################################
#           Routes                       #
##########################################

@main.route('/')
def homepage():
    all_stores = GroceryStore.query.all()
    print(all_stores)
    return render_template('home.html', all_stores=all_stores)

@main.route('/new_store', methods=['GET', 'POST'])
def new_store():
    form = GroceryStoreForm()

    if form.validate_on_submit():
        new_store = GroceryStore(
            title=form.title.data,
            address=form.address.data
        )
        db.session.add(new_store)
        db.session.commit()
        flash('Store was added successfully.')
        return redirect(url_for('main.store_detail', store_id=new_store.id))

    return render_template('new_store.html', form=form)

@main.route('/new_item', methods=['GET', 'POST'])
def new_item():
    form = GroceryItemForm()

    if form.validate_on_submit():
        new_item = GroceryItem(
            name=form.name.data,
            price=form.price.data,
            category=form.category.data,
            photo_url=form.photo_url.data,
            store_id=form.store.data.id
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Item was added successfully.')
        return redirect(url_for('main.item_detail', item_id=new_item.id))

    return render_template('new_item.html', form=form)

@main.route('/store/<store_id>', methods=['GET', 'POST'])
def store_detail(store_id):
    store = GroceryStore.query.get(store_id)
    form = GroceryStoreForm(obj=store)

    if form.validate_on_submit():
        store.title = form.title.data
        store.address = form.address.data
        db.session.commit()
        flash('Store was updated successfully.')
        return redirect(url_for('main.store_detail', store_id=store.id))

    return render_template('store_detail.html', store=store, form=form)

@main.route('/item/<item_id>', methods=['GET', 'POST'])
def item_detail(item_id):
    item = GroceryItem.query.get(item_id)
    form = GroceryItemForm(obj=item)

    if form.validate_on_submit():
        item.name = form.name.data
        item.price = form.price.data
        item.category = form.category.data
        item.photo_url = form.photo_url.data
        item.store_id = form.store.data.id
        db.session.commit()
        flash('Item was updated successfully.')
        return redirect(url_for('main.item_detail', item_id=item.id))

    return render_template('item_detail.html', item=item, form=form)

@main.route('/shopping_list', methods=['GET', 'POST'])
@login_required
def shopping_list():
    form = ShoppingListForm()

    if form.validate_on_submit():
        new_list = ShoppingList(
            name=form.name.data,
            user_id=current_user.id
        )
        db.session.add(new_list)
        db.session.commit()
        flash('Shopping list was created successfully.')
        return redirect(
            url_for('main.shopping_list_detail', list_id=new_list.id)
        )

    lists = ShoppingList.query.filter_by(user_id=current_user.id).all()
    return render_template('shopping_list.html', lists=lists, form=form)

@main.route('/shopping_list/<list_id>', methods=['GET', 'POST'])
@login_required
def shopping_list_detail(list_id):
    shopping_list = ShoppingList.query.get_or_404(list_id)
    if shopping_list.user_id != current_user.id:
        flash('You do not have permission to view this shopping list.')
        return redirect(url_for('main.shopping_list'))

    form = ShoppingListItemForm()

    if form.validate_on_submit():
        # Add item to shopping list with quantity
        stmt = shopping_list_items.insert().values(
            shopping_list_id=shopping_list.id,
            item_id=form.item.data.id,
            quantity=form.quantity.data
        )
        db.session.execute(stmt)
        db.session.commit()
        flash('Item was added to shopping list successfully.')
        return redirect(url_for('main.shopping_list_detail', list_id=list_id))

    return render_template(
        'shopping_list_detail.html',
        shopping_list=shopping_list,
        form=form
    )

@main.route('/shopping_list/<list_id>/delete/<item_id>', methods=['POST'])
@login_required
def delete_shopping_list_item(list_id, item_id):
    shopping_list = ShoppingList.query.get_or_404(list_id)
    if shopping_list.user_id != current_user.id:
        flash('You do not have permission to modify this shopping list.')
        return redirect(url_for('main.shopping_list'))

    # Delete item from shopping list
    stmt = shopping_list_items.delete().where(
        shopping_list_items.c.shopping_list_id == shopping_list.id,
        shopping_list_items.c.item_id == item_id
    )
    db.session.execute(stmt)
    db.session.commit()
    flash('Item was removed from shopping list successfully.')
    return redirect(url_for('main.shopping_list_detail', list_id=list_id))

##########################################
#           Auth Routes                  #
##########################################

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(
            form.password.data
        ).decode('utf-8')
        new_user = User(
            username=form.username.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully.')
        return redirect(url_for('auth.login'))

    return render_template('signup.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(
            user.password, form.password.data
        ):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.homepage'))
        flash('Invalid username or password.')
    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.homepage'))


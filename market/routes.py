from market import app, db, mail
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User, Inventory
from market.forms import (
    ForgotPasswordForm,
    PurchaseItemForm,
    SellItemForm,
    RegisterForm,
    LoginForm,
    ResetPasswordForm
)
from flask_login import login_user, logout_user, login_required, current_user
from flask_mail import Message
import secrets


@app.route('/')
@app.route('/home')
def home_page():
    return render_template('home.html')


@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    sell_form = SellItemForm()

    if request.method == "POST":
        # Handle Purchase
        if purchase_form.validate_on_submit() and "purchased_item" in request.form:
            purchased_item_name = request.form.get('purchased_item')
            item = Item.query.filter_by(name=purchased_item_name).first()

            if item:
                if item.quantity < 1:
                    flash(f"Sorry, {item.name} is out of stock.", category='danger')
                elif current_user.can_purchase(item):
                    # Deduct user budget, reduce item quantity
                    current_user.budget -= item.price
                    item.quantity -= 1

                    # Add item to user's inventory or increment quantity
                    inventory_entry = Inventory.query.filter_by(user_id=current_user.id, item_id=item.id).first()
                    if inventory_entry:
                        inventory_entry.quantity += 1
                    else:
                        new_inventory = Inventory(user_id=current_user.id, item_id=item.id, quantity=1)
                        db.session.add(new_inventory)

                    db.session.commit()
                    flash(f"Congratulations! You purchased {item.name} for ${item.price}", category='success')
                else:
                    flash(f"Not enough funds to buy {item.name}.", category='danger')
            else:
                flash("Item not found.", category='danger')

        # Handle Sell
        elif sell_form.validate_on_submit() and "sold_item" in request.form:
            sold_item_name = request.form.get('sold_item')
            item = Item.query.filter_by(name=sold_item_name).first()

            if item:
                inventory_entry = Inventory.query.filter_by(user_id=current_user.id, item_id=item.id).first()
                if inventory_entry and inventory_entry.quantity > 0:
                    inventory_entry.quantity -= 1
                    current_user.budget += item.price
                    item.quantity += 1

                    # Remove inventory record if quantity zero
                    if inventory_entry.quantity == 0:
                        db.session.delete(inventory_entry)

                    db.session.commit()
                    flash(f"You sold {item.name} for ${item.price}.", category='success')
                else:
                    flash("You don't have this item in your inventory!", category='danger')
            else:
                flash("Item not found.", category='danger')

        # Redirect after POST to avoid form resubmission
        return redirect(url_for('market_page'))

    # GET request: Show available items and user's inventory
    items = Item.query.filter(Item.quantity > 0).all()
    user_inventory = Inventory.query.filter_by(user_id=current_user.id).all()

    return render_template('market.html',
                           items=items,
                           purchase_form=purchase_form,
                           sell_form=sell_form,
                           inventory=user_inventory)


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    form = RegisterForm()
    if form.validate_on_submit():
        user_to_create = User(
            username=form.username.data,
            email_address=form.email_address.data,
            password=form.password1.data
        )
        db.session.add(user_to_create)
        db.session.commit()
        flash(f'Account created successfully for {user_to_create.username}!', category='success')
        return redirect(url_for('market_page'))

    if form.errors:
        for field_name, error_messages in form.errors.items():
            for err in error_messages:
                flash(f"{field_name.capitalize()}: {err}", category='danger')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(username=form.username.data).first()
        if attempted_user and attempted_user.check_password_correction(attempted_password=form.password.data):
            login_user(attempted_user)
            flash(f'Success! You are logged in as: {attempted_user.username}', category='success')
            return redirect(url_for('market_page'))
        else:
            flash('Username and password do not match. Please try again.', category='danger')
    return render_template('login.html', form=form)


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email_address=form.email.data).first()
        if user:
            token = secrets.token_urlsafe(32)
            user.reset_token = token
            db.session.commit()
            reset_url = url_for('reset_password', token=token, _external=True)
            msg = Message('Password Reset Request',
                          recipients=[user.email_address],
                          body=f'Click the link to reset your password: {reset_url}')
            mail.send(msg)
            flash('Password reset link sent to your email.', 'info')
        else:
            flash('No user with that email found.', 'danger')
        return redirect(url_for('login_page'))
    return render_template('forgot_password.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_token=token).first()
    if not user:
        flash("Invalid or expired token.", "danger")
        return redirect(url_for('forgot_password'))

    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password1.data)
        user.reset_token = None
        db.session.commit()
        flash("Your password has been reset successfully.", "success")
        return redirect(url_for("login_page"))

    return render_template("reset_password.html", form=form)


@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for("home_page"))

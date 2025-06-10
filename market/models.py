from market import db, login_manager, bcrypt
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email_address = db.Column(db.String(30), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)  # Increased length for bcrypt hashes
    budget = db.Column(db.Integer, nullable=False, default=1000)
    reset_token = db.Column(db.String(100), nullable=True)

    # ✅ Use Flask-Bcrypt for resetting password
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    # Relationships
    inventory_items = db.relationship('Inventory', back_populates='user', lazy=True)
    owned_items = db.relationship('Item', backref='owner_user', lazy=True)

    @property
    def prettier_budget(self):
        return f"{self.budget:,}$"

    @property
    def password(self):
        raise AttributeError('Password is write-only.')

    # ✅ Use Flask-Bcrypt consistently here too
    @password.setter
    def password(self, plain_text_password):
        self.password_hash = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password_correction(self, attempted_password):
        return bcrypt.check_password_hash(self.password_hash, attempted_password)

    def can_purchase(self, item_obj):
        return self.budget >= item_obj.price


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    barcode = db.Column(db.String(12), nullable=False, unique=True)
    description = db.Column(db.String(1024), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=5)

    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    def __repr__(self):
        return f'<Item {self.name} (${self.price})>'


class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)

    user = db.relationship('User', back_populates='inventory_items')
    item = db.relationship('Item')

    def __repr__(self):
        return f'<Inventory User:{self.user_id} Item:{self.item_id} Qty:{self.quantity}>'

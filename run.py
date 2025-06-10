from market import app, db
from market.models import Item

def seed_database():
    db.create_all()
    if not Item.query.first():
        from market.default_market_data import default_items
        default_items()

if __name__ == '__main__':
    with app.app_context():
        seed_database()
    app.run(debug=True)

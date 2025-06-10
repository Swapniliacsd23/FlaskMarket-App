from market import app, db
from market.models import Item

def default_items():
    items = [
        {'name': 'Laptop', 'price': 800, 'barcode': '123456789012', 'description': 'A powerful laptop for your computing needs.', 'quantity': 5},
        {'name': 'Smartphone', 'price': 500, 'barcode': '987654321098', 'description': 'A sleek smartphone with the latest features.', 'quantity': 10},
    ]

    with app.app_context():
        for item_data in items:
            existing_item = Item.query.filter_by(name=item_data['name']).first()
            if not existing_item:
                item = Item(
                    name=item_data['name'],
                    price=item_data['price'],
                    barcode=item_data['barcode'],
                    description=item_data['description'],
                    owner=None,
                    quantity=item_data['quantity']  # new field
                )
                db.session.add(item)
        
        db.session.commit()
        print("Database seeded with default items.")

if __name__ == '__main__':
    default_items()

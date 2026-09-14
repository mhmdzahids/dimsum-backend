from app.main import create_app
from app.core.db import db_session
from app.modules.products.models import Product

app = create_app()

def seed_products():
    with app.app_context():
        # Drop and recreate the products table to apply schema changes
        engine = db_session.get_bind()
        Product.__table__.drop(engine, checkfirst=True)
        Product.__table__.create(engine)
        
        prod1 = Product(
            name='Dimsum Mini (1 Pax Isi 25 Pcs)',
            description='Dimsum ukuran mini dengan gramasi 18-20 gram, tersaji dalam dua pilihan yaitu per-pax 25 pcs, dan per-mika 150 pcs, cocok untuk acara besar/dijual kembali.',
            weight='18-20 Gram/Pcs',
            category='Dimsum Mini',
            price=25000.00,
            sku='DIMSUM-MINI-PAX-25',
            stock_qty=100,
            is_active=True
        )
        
        prod2 = Product(
            name='Dimsum Mini (1 Mika Isi 150 Pcs)',
            description='Dimsum ukuran mini dengan gramasi 18-20 gram, tersaji dalam dua pilihan yaitu per-pax 25 pcs, dan per-mika 150 pcs, cocok untuk acara besar/dijual kembali.',
            weight='18-20 Gram/Pcs',
            category='Dimsum Mini',
            price=120000.00,
            sku='DIMSUM-MINI-MIKA-150',
            stock_qty=100,
            is_active=True
        )

        prod3 = Product(
            name='Dimsum Jumbo (1 Mika Isi 50 Pcs)',
            description='Dimsum ukuran jumbo dengan gramasi 34-36 gram, berisi 50 pcs cocok untuk acara besar/dijual kembali.',
            weight='34-36 Gram/Pcs',
            category='Dimsum Jumbo',
            price=80000.00,
            sku='DIMSUM-JUMBO-MIKA-50',
            stock_qty=100,
            is_active=True
        )
        
        db_session.add_all([prod1, prod2, prod3])
        db_session.commit()
        print("Database seeded with new Dimsum products!")

if __name__ == '__main__':
    seed_products()

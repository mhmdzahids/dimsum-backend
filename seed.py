from app.main import create_app
from app.core.db import db_session
from app.modules.products.models import Product

app = create_app()

def seed_products():
    with app.app_context():
        # Only seed if no products exist
        existing_count = db_session.query(Product).count()
        if existing_count > 0:
            print("Products already exist. Skipping product seeding.")
            return
        
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

        # Create Admin User
        from app.modules.auth.models import User
        from app.modules.auth.service import AuthService
        
        admin_email = 'admin@dimsum.id'
        existing_admin = db_session.query(User).filter_by(email=admin_email).first()
        if not existing_admin:
            AuthService.register(
                email=admin_email,
                password='password123',
                full_name='Super Admin',
                role='admin'
            )
            print("Default admin user created: admin@dimsum.id / password123")
        else:
            print("Admin user already exists.")

if __name__ == '__main__':
    seed_products()

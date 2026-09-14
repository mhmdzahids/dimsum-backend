from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, declarative_base
from app.core.config import Config

Base = declarative_base()
db_session = scoped_session(sessionmaker())

def init_db(app):
    # Depending on SQLite or MySQL, connection args vary
    # For SQLite, we don't need pool size and overflow for shared hosting, 
    # but for MySQL we would. We'll add a check.
    
    is_sqlite = Config.DATABASE_URL.startswith('sqlite')
    
    engine_kwargs = {}
    if not is_sqlite:
        engine_kwargs = {
            'pool_recycle': 280,
            'pool_pre_ping': True,
            'pool_size': 5,
            'max_overflow': 2,
        }
    else:
        # For SQLite, avoid threading issues
        engine_kwargs = {
            'connect_args': {'check_same_thread': False}
        }
        
    engine = create_engine(Config.DATABASE_URL, **engine_kwargs)
    db_session.configure(bind=engine)
    
    # Import models to ensure they are registered before create_all
    import app.modules.auth.models
    import app.modules.products.models
    import app.modules.orders.models
    import app.modules.payments.models
    import app.modules.inventory.models
    import app.modules.chat.models
    import app.modules.banners.models
    
    Base.metadata.create_all(bind=engine)

def teardown_session(exception=None):
    db_session.remove()

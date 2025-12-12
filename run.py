import os
from app import create_app, db
from app.models import User, Property, Unit, Tenant, Payment

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Context processor pour le shell flask (pratique pour le debug)
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Property': Property,
        'Unit': Unit,
        'Tenant': Tenant,
        'Payment': Payment
    }

if __name__ == '__main__':
    app.run()

from models import db, User, Room, Item
from app import app
from werkzeug.security import generate_password_hash, check_password_hash
with app.app_context():
    db.create_all()
    # Проверяем, есть ли уже суперадмин
    superadmin = User.query.filter_by(username='superadmin').first()
    if not superadmin:
        # Создаем суперадмина
        hashed_password = generate_password_hash('superadmin')
        superadmin = User(username='superadmin', password_hash=hashed_password, role='superadmin')
        db.session.add(superadmin)
        db.session.commit()
        print('Суперадмин создан!')
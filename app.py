from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, Room, Item
from forms import RoomForm, ItemForm, RegistrationForm, LoginForm
from werkzeug.security import generate_password_hash, check_password_hash
import os
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:12345@localhost:5432/postgres'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12345'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
# Функция для проверки роли
def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or not current_user.has_role(role):
                flash('У вас нет прав для доступа к этой странице.', 'danger')
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@app.route('/', methods=['GET', 'POST'])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        return redirect(url_for('rooms')) # Перенаправляем на страницу аудиторий после входа
    return render_template('index.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
@login_required
@role_required('superadmin')  # Доступно только суперадмину
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(username=form.username.data, password_hash=hashed_password, role=form.role.data)  # Use password_hash
        db.session.add(user)
        db.session.commit()
        flash('Аккаунт успешно создан!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Регистрация', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password_hash, form.password.data): #check_password_hash(user.password_hash, form.password.data)
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Неверное имя пользователя или пароль', 'danger')
    return render_template('login.html', title='Войти', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы успешно вышли.', 'info')
    return redirect(url_for('index'))

@app.route('/rooms')
@login_required
def rooms():
    rooms = Room.query.all()
    return render_template('rooms.html', rooms=rooms)

@app.route('/rooms/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_room():
    form = RoomForm()
    if form.validate_on_submit():
        room = Room(name=form.name.data, description=form.description.data)
        db.session.add(room)
        db.session.commit()
        flash('Аудитория успешно добавлена!', 'success')
        return redirect(url_for('rooms'))
    return render_template('create_room.html', title='Добавить аудиторию', form=form)

@app.route('/rooms/<int:room_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_room(room_id):
    room = Room.query.get_or_404(room_id)
    form = RoomForm(obj=room)  # Pre-populate the form with room data
    if form.validate_on_submit():
        room.name = form.name.data
        room.description = form.description.data
        db.session.commit()
        flash('Аудитория успешно обновлена!', 'success')
        return redirect(url_for('rooms'))
    return render_template('edit_room.html', title='Редактировать аудиторию', form=form)


@app.route('/rooms/<int:room_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_room(room_id):
    room = Room.query.get_or_404(room_id)
    db.session.delete(room)
    db.session.commit()
    flash('Аудитория успешно удалена!', 'success')
    return redirect(url_for('rooms'))

@app.route('/items')
@login_required
def items():
    items = Item.query.all()
    return render_template('items.html', items=items)

@app.route('/items/new', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def add_item():
    form = ItemForm()
    if form.validate_on_submit():
        item = Item(type=form.type.data, description=form.description.data,
                    quantity=form.quantity.data, status=form.status.data)
        db.session.add(item)
        db.session.commit()
        flash('Предмет успешно добавлен!', 'success')
        return redirect(url_for('items'))
    return render_template('create_item.html', title='Добавить предмет', form=form)

@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_item(item_id):
    item = Item.query.get_or_404(item_id)
    form = ItemForm(obj=item)
    if form.validate_on_submit():
        item.type = form.type.data
        item.description = form.description.data
        item.quantity = form.quantity.data
        item.status = form.status.data
        db.session.commit()
        flash('Предмет успешно обновлен!', 'success')
        return redirect(url_for('items'))
    return render_template('edit_item.html', title='Редактировать предмет', form=form)

@app.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_item(item_id):
    item = Item.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Предмет успешно удален!', 'success')
    return redirect(url_for('items'))

# Создание базы данных и добавление суперадмина
def create_db_and_admin():
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

if __name__ == '__main__':
    #create_db_and_admin() # Create the DB and the superadmin user
    app.run(debug=True)
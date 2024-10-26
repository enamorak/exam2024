from flask import Flask, render_template, redirect, url_for, flash, request
from flask_migrate import Migrate
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from models import db, Book, Review, User, Role, Genre
from math import ceil
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    title = request.args.get('title')
    genres = request.args.getlist('genres')
    years = request.args.getlist('year')
    volume_from = request.args.get('volume_from')
    volume_to = request.args.get('volume_to')
    author = request.args.get('author')

    # Фильтр по названию
    if title:
        books = books.filter(Book.title.ilike(f'%{title}%'))

    # Фильтр по жанру
    if genres:
        books = books.filter(Book.genres.any(Genre.id.in_(genres)))

    # Фильтр по году
    if years:
        books = books.filter(Book.year.in_(years))

    # Фильтр по объёму
    if volume_from:
        books = books.filter(Book.volume >= volume_from)
    if volume_to:
        books = books.filter(Book.volume <= volume_to)

    # Фильтр по автору
    if author:
        books = books.filter(Book.author.ilike(f'%{author}%'))

    # Сортировка по названию
    books = books.order_by(Book.title)

    # Пагинация
    books = books.paginate(page, per_page=10)

    # Список жанров для мультиселекта
    genres = Genre.query.all()

    # Список годов для мультиселекта
    years = db.session.query(Book.year).distinct().order_by(Book.year).all()

    return render_template('index.html', books=books, genres=genres, years=years)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/book/<int:book_id>')
@login_required
def book_details(book_id):
    book = Book.query.get_or_404(book_id)
    average_rating = book.reviews.aggregate(func.avg(Review.rating))
    reviews = book.reviews.all()
    return render_template('book_details.html', book=book, average_rating=average_rating, reviews=reviews)

@app.route('/add_book', methods=['GET', 'POST'])
@login_required
def add_book():
    if current_user.role.name != 'Администратор':
        flash('У вас недостаточно прав для выполнения данного действия')
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Обработка формы и создание новой книги
        return redirect(url_for('index'))
    return render_template('add_book.html')

@app.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    if current_user.role.name not in ['Администратор', 'Модератор']:
        flash('У вас недостаточно прав для выполнения данного действия')
        return redirect(url_for('index'))
    if request.method == 'POST':
        # Обработка формы и создание новой книги
        return redirect(url_for('index'))
    return render_template('edit_book.html', book=book)

@app.route('/delete_book/<int:book_id>')
@login_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    if current_user.role.name != 'Администратор':
        flash('У вас недостаточно прав для выполнения данного действия')
        return redirect(url_for('index'))
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

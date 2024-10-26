from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(150), nullable=False)
    last_name = db.Column(db.String(150), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    role = db.relationship('Role', backref='users')

    def verify_password(self, password):
        # Проверка пароля
        return True  # Временно
    
class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(150), nullable=False)
    pages = db.Column(db.Integer, nullable=False)
    cover_id = db.Column(db.Integer, db.ForeignKey('cover.id'))
    cover = db.relationship('Cover', backref='book')
    genres = db.relationship('Genre', secondary='book_genre', back_populates='books')
    reviews = db.relationship('Review', backref='book', cascade="all, delete-orphan")

class Cover(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    mime_type = db.Column(db.String(50), nullable=False)
    md5_hash = db.Column(db.String(32), nullable=False)

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    books = db.relationship('Book', secondary='book_genre', back_populates='genres')

book_genre = db.Table('book_genre',
    db.Column('book_id', db.Integer, db.ForeignKey('book.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow) 

with app.app_context():

    db.create_all()

    # Тестовые данные для Role
    roles = [
        Role(name='Администратор', description='Полный доступ к системе'),
        Role(name='Модератор', description='Может редактировать контент'),
        Role(name='Пользователь', description='Стандартный доступ'),
    ]
    db.session.add_all(roles)

    # Тестовые данные для User
    users = [
        User(username='user1', password_hash='hash1', first_name='Иван', last_name='Петров', role=roles[0]),
        User(username='user2', password_hash='hash2', first_name='Мария', last_name='Иванова', role=roles[1]),
        User(username='user3', password_hash='hash3', first_name='Алексей', last_name='Сидоров', role=roles[2]),
        User(username='user4', password_hash='hash4', first_name='Екатерина', last_name='Смирнова', role=roles[0]),
        User(username='user5', password_hash='hash5', first_name='Дмитрий', last_name='Кузнецов', role=roles[1]),
    ]
    db.session.add_all(users)

    # Тестовые данные для Book
    books = [
        Book(title='Властелин колец', description='Эпическая фэнтези-сага', year=1954, publisher='George Allen & Unwin', author='Джон Р. Р. Толкин', pages=1216),
        Book(title='1984', description='Антиутопия о тоталитарном будущем', year=1949, publisher='Secker & Warburg', author='Джордж Оруэлл', pages=328),
        Book(title='Война и мир', description='Исторический роман о России начала XIX века', year=1869, publisher='Русский вестник', author='Лев Толстой', pages=1225),
        Book(title='Мастер и Маргарита', description='Философский роман о Москве 1930-х годов', year=1967, publisher='Московский рабочий', author='Михаил Булгаков', pages=624),
        Book(title='Анна Каренина', description='Роман о любви и общественных условностях', year=1877, publisher='Русский вестник', author='Лев Толстой', pages=848),
    ]
    db.session.add_all(books)

    # Тестовые данные для Cover
    covers = [
        Cover(filename='static/img/cover1.png', mime_type='image/png', md5_hash='hash1'),
        Cover(filename='static/img/cover2.png', mime_type='image/png', md5_hash='hash2'),
        Cover(filename='static/img/cover3.png', mime_type='image/png', md5_hash='hash3'),
        Cover(filename='static/img/cover4.png', mime_type='image/png', md5_hash='hash4'),
        Cover(filename='static/img/cover5.png', mime_type='image/png', md5_hash='hash5'),
    ]
    db.session.add_all(covers)

    # Тестовые данные для Genre
    genres = [
        Genre(name='Фэнтези'),
        Genre(name='Научная фантастика'),
        Genre(name='Исторический роман'),
        Genre(name='Классическая литература'),
        Genre(name='Современная проза'),
    ]
    db.session.add_all(genres)

    books[0].cover = covers[0]
    books[1].cover = covers[1]
    books[2].cover = covers[2]
    books[3].cover = covers[3]
    books[4].cover = covers[4]

    books[0].genres.append(genres[0])
    books[1].genres.append(genres[1])
    books[2].genres.append(genres[2])
    books[3].genres.append(genres[3])
    books[4].genres.append(genres[4])

    # Тестовые данные для Review
    reviews = [
        Review(book=books[0], user=users[0], rating=5, text='Отличная книга!'),
        Review(book=books[1], user=users[1], rating=4, text='Захватывающая история'),
        Review(book=books[2], user=users[2], rating=3, text='Сложный, но интересный роман'),
        Review(book=books[3], user=users[3], rating=5, text='Мастерская проза Булгакова'),
        Review(book=books[4], user=users[4], rating=4, text='Трагическая история любви'),
    ]
    db.session.add_all(reviews)

    db.session.commit()
from flask import Flask, render_template, request, jsonify, redirect, url_for
import redis
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import time
from datetime import datetime
from sqlalchemy.exc import IntegrityError  # Import IntegrityError

app = Flask(__name__)

# Redis Configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# Database Configuration (SQLite for simplicity)
DATABASE_URL = 'sqlite:///./database.db'
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    message = ""
    cache_hit = False
    cache_time = None
    db_time = None
    retrieval_time = None

    if request.method == 'POST':
        username = request.form.get('username')
        if username:
            start_time = time.time()
            # Try to get user data from cache
            cached_user = redis_client.get(f'user:{username}')
            cache_lookup_time = time.time() - start_time
            if cached_user:
                message = f"Retrieved from cache: User data for {username} - {cached_user.decode('utf-8')}"
                cache_hit = True
                cache_time = round(cache_lookup_time * 1000, 2)  # milliseconds
                retrieval_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            else:
                # If not in cache, fetch from the database
                db_start_time = time.time()
                db = next(get_db())
                user = db.query(User).filter(User.username == username).first()
                db_lookup_time = time.time() - db_start_time
                if user:
                    user_data = f"ID: {user.id}, Email: {user.email}"
                    redis_client.setex(f'user:{username}', 30, user_data)  # Cache for 30 seconds
                    message = f"Retrieved from database: User data for {username} - {user_data}"
                    db_time = round(db_lookup_time * 1000, 2)  # milliseconds
                    retrieval_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    message = f"User '{username}' not found."
        else:
            message = "Please enter a username."

    return render_template('index.html', message=message, cache_hit=cache_hit,
                           cache_time=cache_time, db_time=db_time, retrieval_time=retrieval_time)

@app.route('/add_user', methods=['POST'])
def add_user():
    username = request.form.get('new_username')
    email = request.form.get('new_email')
    if username and email:
        db = next(get_db())
        try:
            new_user = User(username=username, email=email)
            db.add(new_user)
            db.commit()
            # Invalidate cache for this user
            redis_client.delete(f'user:{username}')
            return redirect(url_for('index'))  # Redirect to index page
        except IntegrityError:
            db.rollback()  # Rollback the transaction
            message = f"Error: User with username '{username}' already exists."
            return render_template('add_user.html', message=message)
        finally:
            db.close()
    else:
        message = "Please provide both username and email."
        return render_template('add_user.html', message=message)

@app.route('/user/<username>')
def get_user_data(username):
    start_time = time.time()
    cached_user = redis_client.get(f'user:{username}')
    cache_lookup_time = time.time() - start_time

    if cached_user:
        retrieval_method = 'cache'
        user_data = cached_user.decode('utf-8')
        retrieval_time = round(cache_lookup_time * 1000, 2)
    else:
        db_start_time = time.time()
        db = next(get_db())
        user = db.query(User).filter(User.username == username).first()
        db_lookup_time = time.time() - db_start_time
        if user:
            user_data = f"ID: {user.id}, Email: {user.email}"
            redis_client.setex(f'user:{username}', 30, user_data)
            retrieval_method = 'database'
            retrieval_time = round(db_lookup_time * 1000, 2)
        else:
            return jsonify({'error': 'User not found'}), 404
    return jsonify({
        'username': username,
        'data': user_data,
        'retrieval_method': retrieval_method,
        'retrieval_time': retrieval_time,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/create_tables')
def create_tables():
    Base.metadata.create_all(bind=engine)
    return "Database tables created!"

if __name__ == '__main__':
    app.run(debug=True)

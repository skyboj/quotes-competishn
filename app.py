from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

# Настройка БД (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///quotes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модель
class Quote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, default=0)
    times_competed = db.Column(db.Integer, default=0)

@app.before_first_request
def create_tables():
    db.create_all()
    if Quote.query.count() == 0:
        # Подставьте сюда свои 37 цитат
        quotes_list = [
            "Цитата 1", "Цитата 2", "Цитата 3",
            # ...
            # Всего 37
        ]
        for q in quotes_list:
            new_q = Quote(text=q)
            db.session.add(new_q)
        db.session.commit()

@app.route('/')
def index():
    # Проверяем, кому ещё нужно участвовать
    quotes_need_more = Quote.query.filter(Quote.times_competed < 2).all()
    if len(quotes_need_more) < 2:
        return redirect(url_for('results'))

    random_quotes = random.sample(quotes_need_more, 2)
    return render_template('index.html', quote1=random_quotes[0], quote2=random_quotes[1])

@app.route('/vote/<int:winner_id>/<int:loser_id>')
def vote(winner_id, loser_id):
    winner = Quote.query.get_or_404(winner_id)
    loser = Quote.query.get_or_404(loser_id)
    winner.points += 1
    winner.times_competed += 1
    loser.times_competed += 1
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/results')
def results():
    top_quotes = Quote.query.order_by(Quote.points.desc()).limit(18).all()
    return render_template('results.html', quotes=top_quotes)

if __name__ == '__main__':
    # Локальный запуск (необязательный блок — на Heroku работать не помешает)
    app.run(debug=True)

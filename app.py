import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash
from hashids import Hashids


def get_db_connection():
    conn = sqlite3.connect('identifier.sqlite')
    conn.row_factory = sqlite3.Row  # получает строки из БД
    return conn


app = Flask(__name__)
app.config['SECRET_KEY'] = 'try-to-guess'
hashid = Hashids(min_length=4, salt=app.config['SECRET_KEY'])


@app.route('/', methods=['GET', 'POST'])
def index():
    conn = get_db_connection()  # подключаемся к БД
    if request.method == 'POST':
        url = request.form['url']
        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))
        url_data = conn.execute(f'INSERT INTO urls (original_url) VALUES (?)', (url,))
        conn.commit()
        conn.close()

        url_id = url_data.lastrowid
        hash_url = hashid.encode(url_id)
        short_url = request.host_url + hash_url
        return render_template('index.html', s_url=short_url)
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
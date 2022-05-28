from app import app, hashid
from flask import render_template, request, redirect, url_for, flash


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
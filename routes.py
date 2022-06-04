import hashlib
from app import app, hashid, login, db
from flask import render_template, request, redirect, url_for, flash
from models import User, Url
from flask_login import current_user, login_user, logout_user, login_required
from forms import LoginForm, RegistrationForm

@login.user_loader
def load_user(id):
    return User.query.get(id)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        if not url:
            flash('The URL is required!')
            return redirect(url_for('index'))
        hash_link = hashlib.sha256(bytes(url, 'ascii'))
        new_url = Url(
            original_url=url,
            short_url=hash_link.hexdigest()[:5],
            user_id=current_user.id
        )
        db.session.add(new_url)
        db.session.commit()
        return render_template('index.html')
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():  # если форма отправляется
        user = User.query.filter_by(username=form.username.data).first()  # пытаюсь найти пользователя в БД по логину
        if user is None or not user.check_password(form.password.data):
            # если пользователь не найден в БД или пароль не совпал
            return redirect(url_for('login'))  # вернуть пользователя на страницу входа
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Login page', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:  # если пользователь вошел
        return redirect(url_for('index'))  # перенаправим на главную
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db.session.add(user)  # добавить пользователя в БД
        db.session.commit()  # сохранить пользователя в БД
        return redirect(url_for('login'))  # перенаправить на страницу входа
    return render_template('register.html', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    urls = Url.query.filter_by(user_id=user.id)
    return render_template('user.html', user=user, urls=urls)
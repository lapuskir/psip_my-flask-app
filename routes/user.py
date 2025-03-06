from flask import Blueprint, render_template, redirect, flash, url_for, request, current_app
from ..functions import send_email

from ..functions import save_picture
from ..forms import RegistrationForm, LoginForm, ProfileForm
from ..extensions import db, bcrypt
from ..models.user import User
from sqlalchemy import desc
import os
from flask_login import login_user, logout_user, login_required, current_user

user = Blueprint('user', __name__)

@user.route('/user/register', methods=['POST', 'GET'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        avatar_filename = save_picture(form.avatar.data)
        user = User(name=form.name.data, login=form.login.data, avatar=avatar_filename, password=hashed_password)

        try:
            db.session.add(user)
            db.session.commit()
            flash('User registered', 'success')

            # Отправка письма после успешной регистрации
            send_email(
                "Добро пожаловать!",
                user.login,  # Используем login как email
                "Вы успешно зарегистрировались на нашем сайте."
            )

            return redirect(url_for('user.login'))
        except Exception as e:
            print(str(e))
            flash('Error user registered', 'danger')

    return render_template('user/register.html', form=form)


@user.route('/user/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(login=form.login.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f'Вы успешно авторизованы', 'success')
            return redirect(next_page) if next_page else redirect(url_for('shipping.all'))
        else:
            flash(f'Ошибка входа, проверьте логин и пароль ', 'danger')
    return render_template('user/login.html', form=form)


@user.route('/user/logout', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('shipping.all'))


@user.route('/user/profile')
@login_required  # Требует входа в систему
def profile():
    return render_template('post/profile.html', user=current_user)


@user.route('/user/all_profile')
@login_required
def all_profile():
    users = User.query.order_by(desc(User.date)).all()
    return render_template('user/all_profile.html', users=users)


@user.route('/user/<int:id>/update_user_profile', methods=['POST', 'GET'])
@login_required
def update_user_profile(id):
    user = User.query.get(id)
    if not user:
        flash("Пользователь не найден", "danger")
        return redirect('/')

    form = ProfileForm()
    if form.validate_on_submit():
        user.name = form.name.data
        user.login = form.login.data

        # Проверяем загрузку нового аватара
        if form.avatar.data:
            user.avatar = save_picture(form.avatar.data)

        # ЛОГИРУЕМ ЗНАЧЕНИЕ ПЕРЕД СОХРАНЕНИЕМ
        print(f"Аватар перед коммитом: {user.avatar}")

        db.session.commit()
        flash("Профиль успешно обновлён!", "success")
        return redirect(url_for('user.update_user_profile', id=user.id))

    return render_template('user/update_user_profile.html', user=user, form=form)


@user.route('/user/<int:id>/delete_user', methods=['POST', 'GET' ])
@login_required
def delete_user(id):
        user = User.query.get(id)
        try:
            db.session.delete(user)
            db.session.commit()
            return redirect('/user/all_profile')
        except Exception as e:
            print(str(e))
            return str(e)

@user.route('/search', methods=['GET'])
def search():
    search_query = request.args.get('search_query', '').strip()
    # Логика поиска по пользователям
    users = User.query.filter(User.name.ilike(f'%{search_query}%')).all()
    return render_template('user/all_profile.html', users=users)







from flask import render_template, redirect, url_for, flash, Blueprint, jsonify, request
from flask_login import login_required
from ..forms import EmployeeForm
from ..models.employee import Employee
from ..extensions import db
from werkzeug.security import generate_password_hash
from ..functions import save_picture
from sqlalchemy import desc
employee = Blueprint('employee', __name__)  # Убираем дублирование


@employee.route('/employee_register', methods=['GET', 'POST'])
@login_required
def register_employee():
    form = EmployeeForm()  # Используем правильное имя формы
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)

        # Сохраняем аватар
        avatar_filename = save_picture(form.avatar.data) if form.avatar.data else None

        # Создаем нового сотрудника
        new_employee = Employee(
            name=form.name.data,
            login=form.login.data,
            position=form.position.data,
            password=hashed_password,
            avatar=avatar_filename
        )

        try:
            db.session.add(new_employee)
            db.session.commit()
            flash(f'Сотрудник {form.name.data} зарегистрирован', 'success')
            return redirect(url_for('employee.register_employee'))
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при регистрации сотрудника: {str(e)}', 'danger')

    return render_template('employee/employee_register.html', form=form)


@employee.route('/check_login/<login>', methods=['GET'])
def check_login(login):
    # Проверяем, существует ли сотрудник с таким логином
    existing_employee = Employee.query.filter_by(login=login).first()
    if existing_employee:
        return jsonify({"exists": True})  # Логин уже занят
    else:
        return jsonify({"exists": False})  # Логин свободен

@employee.route('/employee/all_employee', methods=['GET'])
@login_required
def all_employee():
    search_query = request.args.get('search_query', '')  # Получаем запрос из URL
    if search_query:
        employees = Employee.query.filter(
            (Employee.name.ilike(f'%{search_query}%')) |
            (Employee.login.ilike(f'%{search_query}%')) |
            (Employee.position.ilike(f'%{search_query}%'))
        ).all()
    else:
        employees = Employee.query.order_by(desc(Employee.date_hired)).all()  # Если поиска нет, выводим всех сотрудников

    return render_template('employee/all_employee.html', employees=employees)


@employee.route('/employee/<int:id>/update_employee_profile', methods=['GET', 'POST'])
@login_required
def update_employee_profile(id):
    # Получаем сотрудника по id
    employee = Employee.query.get(id)
    if not employee:
        flash("Сотрудник не найден", "danger")
        return redirect(url_for('employee.all_employee'))

    form = EmployeeForm(obj=employee)  # Передаем объект сотрудника в форму

    if form.validate_on_submit():
        employee.name = form.name.data
        employee.login = form.login.data
        employee.position = form.position.data

        # Если загружен новый аватар
        if form.avatar.data:
            employee.avatar = save_picture(form.avatar.data)

        db.session.commit()
        flash("Профиль сотрудника успешно обновлен!", "success")
        return redirect(url_for('employee.update_employee_profile', id=employee.id))

    return render_template('employee/update_employee_profile.html', employee=employee, form=form)


@employee.route('/employee/<int:id>/delete', methods=['POST'])
@login_required
def delete_employee(id):
    employee = Employee.query.get(id)
    if not employee:
        flash("Сотрудник не найден", "danger")
        return redirect(url_for('employee.all_employee'))

    try:
        db.session.delete(employee)
        db.session.commit()
        flash(f'Сотрудник {employee.name} удален.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении сотрудника: {str(e)}', 'danger')

    return redirect(url_for('employee.all_employee'))




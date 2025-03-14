from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import current_user, login_required
from datetime import datetime, timedelta
from pytz import timezone, utc
from ..extensions import db
from ..models.shipping import Shipping
from ..models.employee import Employee
from sqlalchemy import desc, or_
import pandas as pd
from io import BytesIO
shipping = Blueprint('shipping', __name__)


@shipping.route('/')
def some_page():
    shippings = Shipping.query.order_by(desc(Shipping.date)).all()
    if not current_user.is_authenticated:
        return redirect(url_for('user.register'))  # Перенаправляем на регистрацию
    return render_template('post/all.html', shippings=shippings)  # Если авторизован — показываем контент


@shipping.route('/', methods=['GET', 'POST'])
@login_required
def all():
    shippings = Shipping.query.order_by(desc(Shipping.date)).all()

    msk_tz = timezone('Europe/Moscow')  # Московский часовой пояс

    for shipping in shippings:
        # Если время без временной зоны, предполагаем, что оно в UTC
        if shipping.date.tzinfo is None:
            # Локализуем дату как UTC, если она без временной зоны
            shipping.date = utc.localize(shipping.date)
        else:
            # Если дата уже с временной зоной, проверим её
            if shipping.date.tzinfo != msk_tz:
                # Если временная зона не Московская, переводим в Московский часовой пояс
                shipping.date = shipping.date.astimezone(msk_tz)

    return render_template('post/all.html', shippings=shippings)


@shipping.route('/shiping/create', methods=['POST', 'GET' ])
@login_required
def create():
    if request.method == 'POST':
        # Получаем данные из формы
        shipping_name = request.form['shipping_name']
        driver_id = request.form['driver']  # Получаем id выбранного водителя
        vehicle = request.form['vehicle']
        starting_point = request.form['starting_point']
        destination_point = request.form['destination_point']
        author_shipping_name = request.form['author_shipping_name']  # Получаем значение из формы

        # Создаем новую отгрузку
        shipping = Shipping(
            shipping_name=shipping_name,
            driver_id=driver_id,  # Привязываем выбранного водителя
            vehicle=vehicle,
            starting_point=starting_point,
            destination_point=destination_point,
            author_shipping_name=author_shipping_name
        )

        try:
            db.session.add(shipping)
            db.session.commit()
            flash('Отгрузка успешно создана!', 'success')
            return redirect(url_for('shipping.all'))  # Перенаправляем на страницу всех отгрузок
        except Exception as e:
            db.session.rollback()
            flash(f'Произошла ошибка при создании отгрузки: {str(e)}', 'danger')

    else:
        # Получаем всех водителей из базы
        drivers = Employee.query.filter_by(position='Водитель').all()
        return render_template('post/create.html', drivers=drivers)


@shipping.route('/shiping/<int:id>/update', methods=['POST', 'GET' ])
@login_required
def update(id):

    shipping = Shipping.query.get(id)
    if request.method == 'POST':
        shipping.shipping_name = request.form['shipping_name']
        shipping.driver = request.form['driver']
        shipping.vehicle = request.form['vehicle']
        shipping.starting_point = request.form['starting_point']
        shipping.destination_point = request.form['destination_point']
        shipping.author_shipping_name = current_user.name




        try:
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(str(e))
    else:
        return render_template('post/update.html', shipping=shipping)


@shipping.route('/shiping/<int:id>/delete', methods=['POST', 'GET' ])
@login_required
def delete(id):
        shipping = Shipping.query.get(id)
        try:
            db.session.delete(shipping)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(str(e))
            return str(e)


@shipping.route('/search', methods=['GET'])
@login_required
def search():
    search_query = request.args.get('search_query', '').strip()  # Убираем лишние пробелы по краям
    filter_type = request.args.get('filter_type', '')  # Получаем фильтр, если он выбран

    # Если в поисковом запросе есть данные
    if search_query:
        search_terms = search_query.split()  # Разделяем строку на отдельные термины

        # Формируем условие фильтрации для каждого слова в запросе
        filters = []
        for term in search_terms:
            if filter_type:
                # Если выбран фильтр по конкретному столбцу
                filters.append(
                    getattr(Shipping, filter_type).ilike(f'%{term}%')
                )
            else:
                # Если фильтра по столбцу нет, ищем по всем столбцам
                filters.append(
                    or_(
                        Shipping.shipping_name.ilike(f'%{term}%'),
                        Shipping.driver.ilike(f'%{term}%'),
                        Shipping.destination_point.ilike(f'%{term}%'),
                        Shipping.starting_point.ilike(f'%{term}%'),
                        Shipping.vehicle.ilike(f'%{term}%')
                    )
                )

        # Применяем фильтрацию с несколькими условиями
        shippings = Shipping.query.filter(
            or_(*filters)  # Разворачиваем список фильтров
        ).order_by(desc(Shipping.date)).all()
    else:
        # Если поисковый запрос пустой, выводим все отгрузки
        if filter_type:
            shippings = Shipping.query.filter(
                getattr(Shipping, filter_type).ilike(f'%{search_query}%')
            ).order_by(desc(Shipping.date)).all()
        else:
            # Без фильтрации
            shippings = Shipping.query.order_by(desc(Shipping.date)).all()

    return render_template('post/all.html', shippings=shippings)


@shipping.route('/filter', methods=['GET'])
@login_required
def filter():
    filter_type = request.args.get('filter_type', '').strip()  # Получаем тип фильтрации

    if filter_type == 'latest':
        # Фильтрация по последним отгрузкам
        shippings = Shipping.query.order_by(desc(Shipping.date)).all()

    elif filter_type == 'oldest':
        # Фильтрация по старым отгрузкам
        shippings = Shipping.query.order_by(Shipping.date).all()

    elif filter_type == 'this_week':
        # Фильтрация по отгрузкам за текущую неделю
        today = datetime.utcnow()
        start_of_week = today - timedelta(days=today.weekday())  # Начало недели
        shippings = Shipping.query.filter(Shipping.date >= start_of_week).order_by(desc(Shipping.date)).all()

    elif filter_type == 'by_driver':
        # Фильтрация по водителю
        driver_name = request.args.get('driver_name', '').strip()
        if driver_name:
            shippings = Shipping.query.filter(Shipping.driver.ilike(f'%{driver_name}%')).order_by(
                desc(Shipping.date)).all()
        else:
            shippings = Shipping.query.order_by(desc(Shipping.date)).all()

    elif filter_type == 'by_shipping_name':
        # Фильтрация по перевозчику
        shipping_name = request.args.get('shipping_name', '').strip()
        if shipping_name:
            shippings = Shipping.query.filter(Shipping.shipping_name.ilike(f'%{shipping_name}%')).order_by(
                desc(Shipping.date)).all()
        else:
            shippings = Shipping.query.order_by(desc(Shipping.date)).all()

    else:
        # Если фильтра не выбран, выводим все отгрузки
        shippings = Shipping.query.order_by(desc(Shipping.date)).all()

    return render_template('post/all.html', shippings=shippings)


@shipping.route('/export_excel', methods=['GET'])
@login_required
def export_excel():
    # Получаем все отгрузки
    shippings = Shipping.query.all()

    # Формируем данные для экспорта
    data = []
    for shipping in shippings:
        data.append({
            "ID": shipping.id,
            "Перевозчик": shipping.shipping_name,
            "Водитель": shipping.driver.name if shipping.driver else "Не назначен",
            "Точка отправления": shipping.starting_point,
            "Точка назначения": shipping.destination_point,
            "Транспортное средство": shipping.vehicle,
            "Дата": shipping.date.strftime('%d.%m.%Y %H:%M'),
            "Старший отгрузки (ID)": shipping.author_shipping_name
        })

    # Создаем DataFrame
    df = pd.DataFrame(data)

    # Создаем файл в памяти
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Отгрузки")

    output.seek(0)  # Перематываем указатель в начало

    # Возвращаем файл пользователю
    response = Response(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response.headers["Content-Disposition"] = "attachment; filename*=UTF-8''Отгрузки.xlsx"

    return response
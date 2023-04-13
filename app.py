from flask import Flask, render_template, request, redirect, abort
from forms.link_forms import LinkForm, LinkFormSearch
from forms.LoginForm import LoginForm
from forms.RegisterForm import RegisterForm
from data.users import User
from sqlalchemy import and_, desc, asc
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from data.links import Link

import urllib.parse
from flask_paginate import Pagination, get_page_parameter
from flask import session as sess_client

from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)

db_session.global_init("db/db.db")

db_sess = db_session.create_session()


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/set_sort')
def set_sort():
    sess_client['sort_order'] = request.args.get('order', 'desc')
    path = request.environ.get('HTTP_REFERER')
    if path:
        return redirect(path)
    else:
        return redirect('/')


@app.route("/", methods=['GET', 'POST'])
def links():
    report_msg = None
    search_form = LinkFormSearch()

    links = []

    pagination = None

    order = 'desc'

    if request.method == 'GET':
        page = request.args.get(get_page_parameter(), type=int, default=1)

        limit = 2
        total = db_sess.query(Link).count()

        offset = (page - 1) * limit

        order = sess_client.get('sort_order', 'desc')

        if order == 'asc':
            links = db_sess.query(Link).order_by(asc(Link.id)).offset(offset).limit(limit).all()
        elif order:
            links = db_sess.query(Link).order_by(desc(Link.id)).offset(offset).limit(limit).all()

        pagination = Pagination(page=page, per_page=limit, total=total,
                                record_name='links',
                                css_framework='foundation')

    elif request.method == 'POST':
        search_values = [(key, val) for key, val in search_form.data.items() if
                         key in ['link', 'title', 'comment'] and val.strip()]

        if search_values:
            links = db_sess.query(Link).filter(
                and_(*(getattr(Link, field).like(f'%{value}%') for field, value in search_values))).all()
        if not search_values:
            report_msg = 'Не заданы условия поиска'
    return render_template('links.html', links=links, search_form=search_form, report_msg=report_msg,
                           pagination=pagination, order=order)


@app.route('/links', methods=['POST', 'GET'])
@login_required
def link_add():
    link_form = LinkForm()
    if link_form.validate_on_submit():
        db_sess = db_session.create_session()
        Links = Link()
        Links.link = link_form.link.data
        Links.title = link_form.title.data
        Links.comment = link_form.comment.data
        Links.is_private = link_form.is_private.data
        current_user.news.append(Links)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('link_add.html', title='Добавление ссылки',
                           link_form=link_form)




@app.route('/links/<int:link_id>', methods=['POST', 'GET'])
@login_required
def link_edit(link_id):
    link_form = LinkForm()

    if request.method == 'GET':
        db_sess = db_session.create_session()
        link = db_sess.query(Link).filter(Link.id == link_id, Link.user == current_user).first()
        if link:
            link_form.link.data = link.link
            link_form.title.data = link.title
            link_form.comment.data = link.comment
            link_form.is_private.data = link.is_private
        else:
            abort(404)
    if link_form.validate_on_submit():
        db_sess = db_session.create_session()
        link = db_sess.query(Link).filter(Link.id == link_id,
                                          Link.user == current_user
                                          ).first()
        if link:
            link.link = link_form.link.data
            link.title = link_form.title.data
            link.comment = link_form.comment.data
            link.is_private = link_form.is_private.data
            db_sess.commit()
            return redirect('/')
        else:
            abort(404)
    # if request.method == 'POST':
    #     if link_form.validate_on_submit():
    #         if link_id:
    #             # изменение данных ссылки в БД
    #             link = db_sess.query(Link).filter(Link.id == link_id).first()
    #             if link:
    #                 link.link = urllib.parse.unquote(link_form.link.data)
    #                 link.title = link_form.title.data
    #                 link.comment = link_form.comment.data
    #             else:
    #                 abort(404)
    #         else:
    #             # Добавление данных ссылки к бд
    #             link = Link(
    #                 link=urllib.parse.unquote(link_form.link.data),
    #                 title=link_form.title.data,
    #                 comment=link_form.comment.data)
    #             db_sess.add(link)
    #         db_sess.commit()
    #         return redirect('/')
    return render_template('link_add.html', title='Редактирование ссылки', link_form=link_form)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            nickname=form.nickname.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/link_delete/<int:link_id>')
def link_delete(link_id):
    link = db_sess.query(Link).filter(Link.id == link_id).first()
    if link:
        db_sess.delete(link)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/get_title', methods=['POST', 'GET'])
def get_title():
    return 'Заголовок страницы'


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1', debug=True)

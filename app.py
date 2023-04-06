from flask import Flask, render_template, request, redirect, abort
from forms.link_forms import LinkForm, LinkFormSearch
from sqlalchemy import and_, desc, asc

from data.links import Link

import urllib.parse
from flask_paginate import Pagination, get_page_parameter
from flask import session as sess_client

from data import db_session

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/db.db")

db_sess = db_session.create_session()


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


@app.route('/link_add', methods=['POST', 'GET'])
@app.route('/link_edit/<int:link_id>', methods=['POST', 'GET'])
def links_manage(link_id=None):
    link_form = LinkForm()

    if request.method == 'GET' and link_id:
        link = db_sess.query(Link).filter(Link.id == link_id).first()
        if link:
            link_form.link.data = link.link
            link_form.title.data = link.title
            link_form.comment.data = link.comment
        else:
            abort(404)

    if request.method == 'POST':
        if link_form.validate_on_submit():
            if link_id:
                # изменение данных ссылки в БД
                link = db_sess.query(Link).filter(Link.id == link_id).first()
                if link:
                    link.link = urllib.parse.unquote(link_form.link.data)
                    link.title = link_form.title.data
                    link.comment = link_form.comment.data
                else:
                    abort(404)
            else:
                # Добавление данных ссылки к бд
                link = Link(
                    link=urllib.parse.unquote(link_form.link.data),
                    title=link_form.title.data,
                    comment=link_form.comment.data)
                db_sess.add(link)
            db_sess.commit()
            return redirect('/')
    return render_template('link_add.html', link_id=link_id, link_form=link_form)


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

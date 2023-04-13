from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, BooleanField
from wtforms.validators import DataRequired, URL


class LinkForm(FlaskForm):
    link = TextAreaField('Ссылка:', validators=[DataRequired(), URL(message="Неправильный формат ссылки")])
    title = TextAreaField('Заголовок:', validators=[DataRequired()])
    comment = TextAreaField('Комментарий:')
    is_private = BooleanField("Личное")

    link_submit = SubmitField()


class LinkFormSearch(FlaskForm):
    link = StringField('Ссылка:')
    title = StringField('Заголовок:')
    comment = StringField('Комментарий:')

    search_submit = SubmitField()

from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, StringField, BooleanField, validators, SelectField
from wtforms.validators import DataRequired, URL


def custom_validator(form, field):
    if len(field.data) > 70:
        raise validators.ValidationError('Input must be less than 70 characters long')


class LinkForm(FlaskForm):
    link = TextAreaField('Ссылка:',
                         validators=[DataRequired(), URL(message="Неправильный формат ссылки"), custom_validator])
    title = TextAreaField('Заголовок:', validators=[DataRequired()])
    comment = TextAreaField('Комментарий:')
    category = SelectField("Категория:", choices=["Спорт", "Новости", "Путешествия", "Самообразование",
                                                  "Програмирование", "Новости", "Фильмы"], default="Новости")
    is_private = BooleanField("Личное")

    link_submit = SubmitField()


class LinkFormSearch(FlaskForm):
    link = StringField('Ссылка:')
    title = StringField('Заголовок:')
    comment = StringField('Комментарий:')
    category = SelectField("Категория:", choices=["Спорт", "Новости", "Путешествия", "Самообразование",
                                                  "Програмирование", "Новости", "Фильмы"], default="Новости")

    search_submit = SubmitField()

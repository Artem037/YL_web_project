from datetime import datetime
import sqlalchemy
from sqlalchemy import orm


from .db_session import SqlAlchemyBase


class Link(SqlAlchemyBase):
    __tablename__ = 'links'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True,
                           autoincrement=True)
    link = sqlalchemy.Column(sqlalchemy.Text, nullable=False)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    comment = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    is_private = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    created_date = sqlalchemy.Column(sqlalchemy.Date,
                                     default=datetime.now().date)

    user_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("users.id"))
    user = orm.relationship('User')

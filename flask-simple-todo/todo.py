#!/usr/bin/env python
#coding:utf-8

import os
from datetime import datetime

from flask import Flask, Blueprint, render_template, url_for, redirect, flash, request
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.wtf import Form
from wtforms import TextField, SubmitField, ValidationError
from wtforms.validators import Required


DEBUG = True
SECRET_KEY = '\xca\x8dh\\o\x8f\xfc\xc4\x92\xf5\xc3\x8e\xbc\xba/37|X\xb7\xb7\t^\x98'
SQLALCHEMY_DATABASE_URI = 'sqlite:///todo.sqlite'

app = Flask(__name__)
app.config.from_object(__name__)
db = SQLAlchemy(app)
db.init_app(app)
todoapp = Blueprint('todoapp', __name__, template_folder='templates',
                    static_folder='static', url_prefix='/todo')

class Todo(db.Model):
    '''数据模型'''

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    posted_on = db.Column(db.Date, default=datetime.utcnow)
    status = db.Column(db.Boolean(), default=False)

    def __init__(self, *args, **kwargs):
        super(Todo, self).__init__(*args, **kwargs)

    def __repr__(self):
        return "<Todo '%s'>" % self.title

    def store_to_db(self):
        '''保存数据到数据库'''

        db.session.add(self)
        db.session.commit()

    def delete_todo(self):
        '''删除数据'''

        db.session.delete(self)
        db.session.commit()

class TodoForm(Form):
    '''表单'''

    title = TextField(u"内容", validators=[Required(message=u"任务内容")])


@todoapp.route('/', methods=['GET', 'POST'])
def index():
    todo = Todo.query.order_by('-id')
    form = TodoForm(request.form)
    if request.method == 'POST' and form.validate_on_submit():
        t = Todo(title=form.title.data)
        try:
            t.store_to_db()
            flash(u"添加成功")
            return redirect(request.args.get('next') or url_for('.index'))
        except:
            flash(u'存储失败！')

    return render_template('index.html', todo=todo, form=form)

@todoapp.route('/<int:id>/del')
def tdel(id):
    todo = Todo.query.filter_by(id=id).first()
    if todo:
        todo.delete_todo()
    flash(u"记录删除成功")
    return redirect(url_for('.index'))

@todoapp.route('/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    todo = Todo.query.filter_by(id=id).first()
    form = TodoForm(title=todo.title)
    if request.method == 'POST' and form.validate_on_submit():
        Todo.query.filter_by(id=id).update({Todo.title:request.form['title']})
        db.session.commit()
        flash(u"记录编辑成功")
        return redirect(url_for('.index'))

    return render_template('edit.html', todo=todo, form=form)

@todoapp.route('/<int:id>/done')
def done(id):
    todo = Todo.query.filter_by(id=id).first()
    if todo:
        Todo.query.filter_by(id=id).update({Todo.status:True})
        db.session.commit()
        flash(u"任务完成")

    return redirect(url_for('.index'))

@todoapp.route('/<int:id>/redo')
def redo(id):
    todo = Todo.query.filter_by(id=id).first()
    if todo:
        Todo.query.filter_by(id=id).update({Todo.status:False})
        flash(u"记录重置成功")
        db.session.commit()

    return redirect(url_for('.index'))

@todoapp.errorhandler(404)
def page_not_found(error):
    return render_template('page_404.html'), 404

app.register_blueprint(todoapp)

if __name__ == '__main__':
    app.run()

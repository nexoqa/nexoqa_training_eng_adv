from MySQLdb import converters, connect, FIELD_TYPE
from flask import Flask, send_from_directory, jsonify, request
import wtforms_json
import sqlite3
wtforms_json.init()
from wtforms import Form
from wtforms.fields import TextField
from wtforms.validators import DataRequired
# DATABASE


def dict_factory(cursor, row):
  d = {}
  for idx, col in enumerate(cursor.description):
    d[col[0]] = row[idx]
  return d

class DB:
  connection = None
  @staticmethod
  def connect():
    # Custom converter for tinyint to boolean
    conv = converters.conversions
    def bool_decoder(val):
      if int(val) == 0:
        return False
      return True
    conv[FIELD_TYPE.TINY]= bool_decoder
    DB.connection = sqlite3.connect('example.db', check_same_thread=False)
    DB.connection.row_factory = dict_factory
    DB.cursor = DB.connection.cursor()

  @staticmethod
  def select(query, clazz, as_dict=False):
    DB.cursor.execute(query)
    db_result = DB.cursor.fetchall()
    if as_dict:
      return[dict(row) for row in db_result]
    result = []
    for row in db_result:
      data = clazz()
      for key in row.keys():
        if key == "id":
          data._id = row[key]
        else:
          data.__setattr__(key, row[key])
      result.append(data)
    return result
  
  @staticmethod
  def insert(query):
    DB.cursor.execute(query)
    DB.connection.commit()
    return DB.cursor.lastrowid

  @staticmethod
  def update(query):
    DB.cursor.execute(query)
    DB.connection.commit()

# TODO

class Todo(object):
  def __init__(self, _id=-1, title=None, description=None, created_at=None, modified_at=None, is_done=False):
    self._id = _id
    self.title = title
    self.description = description
    self.created_at = created_at
    self.modified_at = modified_at
    self.is_done = is_done

  @property
  def id(self):
    return self._id

  @classmethod
  def select_all(cls, as_dict=False):
    query = """
    select 
      id, title, description, created_at, modified_at, is_done 
    from todo_list 
    order by created_at desc;
    """
    return DB.select(query, Todo, as_dict)
  
  @classmethod
  def select_one(cls, _id, as_dict=False):
    query = """
    select 
      id, title, description, created_at, modified_at, is_done 
    from todo_list 
    where id = %s
    """ % _id
    return DB.select(query, Todo, as_dict)[0]

  def insert(self):
    query = """
    INSERT INTO todo_list 
      (title, description, created_at) 
    VALUES ('%s', '%s', CURRENT_TIMESTAMP);
    """ % (self.title, self.description)
    self._id = DB.insert(query)

  def update(self, title, description):
    query = """
    UPDATE todo_list 
      set title='%s', 
      description='%s', 
      modified_at=CURRENT_TIMESTAMP
    WHERE id = %s
    """ % (title, description, self.id)
    DB.update(query)
    self.title = title
    self.description = description

  def set_done(self):
    query = """
    UPDATE todo_list 
      set is_done = 1, 
      modified_at=CURRENT_TIMESTAMP
    WHERE id = %s
    """ % (self.id)
    DB.update(query)
    self.is_done = True

  def set_todo(self):
    query = """
    UPDATE todo_list 
      set is_done = 0, 
      modified_at=CURRENT_TIMESTAMP
    WHERE id = %s
    """ % (self.id)
    DB.update(query)
    self.is_done = False

  def __repr__(self):
    return "Todo(id=%s, title=%s, description=%s, created_at=%s, modified_at=%s, is_done=%s)\n" % (self._id, self.title, self.description, self.created_at, self.modified_at, self.is_done)

  def as_dict(self):
    out = {}
    for key in ["id", "title", "description", "created_at", "modified_at", "is_done"]:
      out[key] = getattr(self, key)
    return out

# WTForm
class TodoPost(Form):
  title = TextField('title', validators=[DataRequired()])
  description = TextField('description', validators=[DataRequired()])

class TodoPut(Form):
  title = TextField('title')
  description = TextField('description')

# FLASK
app = Flask(__name__)
@app.route("/")
def index():
  return send_from_directory("static", "index.html")

@app.route("/todo")
def todo_list():
  todo_list = Todo.select_all(as_dict=True) 
  return jsonify(todo_list)

@app.route("/todo/<int:todo_id>")
def todo_one(todo_id):
  todo = Todo.select_one(todo_id, as_dict=True) 
  return jsonify(todo)

@app.route("/todo", methods=["post"])
def todo_post():
  todo_form = TodoPost.from_json(request.json, skip_unknown_keys=False) 
  if todo_form.validate():
    todo = Todo(title=todo_form.title.data, description=todo_form.description.data)
    todo.insert()
    return jsonify(todo.as_dict())
  raise

@app.route("/todo/<int:todo_id>", methods=["put"])
def todo_put(todo_id):
  todo = Todo.select_one(todo_id)
  todo_form = TodoPut.from_json(request.json, skip_unknown_keys=False)  
  if todo_form.validate():
    todo.update(title=todo_form.title.data or todo.title, 
      description=todo_form.description.data or todo.description)
    return jsonify(todo.as_dict())
  raise

@app.route("/todo/<int:todo_id>/check")
def todo_check(todo_id):
  todo = Todo.select_one(todo_id)
  todo.set_done()
  return jsonify({"ok": True})

@app.route("/todo/<int:todo_id>/uncheck")
def todo_uncheck(todo_id):
  todo = Todo.select_one(todo_id)
  todo.set_todo()
  return jsonify({"ok": True})

if __name__ == "__main__":  
  DB.connect()
  app.run(host="0.0.0.0", port=5001, debug=True)



"CREATE TABLE `todo_list` (`id` int(11) NOT NULL AUTO_INCREMENT,`title` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,`description` text COLLATE utf8mb4_unicode_ci,`created_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',`modified_at` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',`is_done` tinyint(1) DEFAULT '0',PRIMARY KEY (`id`)"


"create table todo_list_test (id INTEGER NOT NULL AUTOINCREMENT, tittle text, description text, timestamp NOT NULL DEFAULT '0000-00-00 00:00:00', modified_at NOT NULL DEFAULT '0000-00-00 00:00:00', is_done integer DEFAULT 0, PRIMARY KEY (id))"



"""
CREATE TABLE todo_list (
id INTEGER PRIMARY KEY AUTOINCREMENT,
title TEXT NOT NULL,
description TEXT NOT NULL,
created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
modified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
is_done INTEGER DEFAULT 0
);
"""

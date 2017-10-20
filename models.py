
import datetime
import os

import peewee
from playhouse.db_url import connect

DB = connect(
  os.environ.get(
    'DATABASE_URL',
    'postgres://localhost:5432/mindCloud'
  )
)

class BaseModel (peewee.Model):
  class Meta:
    database = DB

class Person (BaseModel):
  brain_id = peewee.PrimaryKeyField(unique = True)
  name = peewee.CharField(max_length=60)
  token = peewee.TextField()


  def __str__ (self):
    return self.name


class Goals (BaseModel):
  person = peewee.ForeignKeyField(Person, null=True)
  title = peewee.CharField(max_length=60)
  achievement = peewee.TextField()
  slug = peewee.CharField(max_length=50, unique=True)
  reminder = peewee.DateTimeField(
            default=datetime.datetime.utcnow)

  def __str__ (self):
    return self.Person
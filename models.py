
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

class MindCloud (BaseModel):
  id = peewee.PrimaryKeyField(unique = True)
  city = peewee.CharField(max_length=60)
  data = peewee.TextField()
  created = peewee.DateTimeField(
            default=datetime.datetime.utcnow)

  def __str__ (self):
    return self.created

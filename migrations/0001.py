import models

def forward ():
  models.DB.create_tables([models.Person, models.Goals])

if __name__ == '__main__':
  forward()

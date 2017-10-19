import models

def forward ():
  models.DB.create_tables([models.MindCloud])

if __name__ == '__main__':
  forward()

import os 

from app import app, db
from flask_script import Manager, Server 
from flask_migrate import Migrate, MigrateCommand 

app.config.from_object(os.environ["APP_SETTINGS"])
manager = Manager(app)
migrate = Migrate(app,db)

manager.add_command("runserver", Server(host="0.0.0.0", port=9000))
manager.add_command('db', MigrateCommand) 

if __name__ == '__main__':
    manager.run()
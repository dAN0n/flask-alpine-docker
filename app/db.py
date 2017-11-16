#!/usr/bin/python
from flask_migrate import init, migrate, upgrade, downgrade
from app import app
import sys, datetime

# Look at https://stackoverflow.com/a/31140916 if drop/alter not work
# Always check generated migrations manually!!!

def db_init():
    with app.app_context():
        init()

def db_migrate():
    now = datetime.datetime.now()
    with app.app_context():
        migrate(message="{}_{}_{}_{}_{}".format(now.day, now.month, now.year, now.hour, now.minute))

def db_upgrade():
    with app.app_context():
        upgrade()

def db_downgrade():
    with app.app_context():
        downgrade()

def help_message():
    print("""Usage: python migrate.py [init|migrate|upgrade|downgrade|help]

COMMANDS:
help\t\tshow this help message and exit.
init\t\tinitializes migration support for the application.
migrate\t\tcreates an automatic revision script.
upgrade\t\tupgrades the database to last revision.
downgrade\tdowngrades the database by 1 revision.""")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            db_init()
        elif sys.argv[1] == "migrate":
            db_migrate()
        elif sys.argv[1] == "upgrade":
            db_upgrade()
        elif sys.argv[1] == "downgrade":
            db_downgrade()
        else:
            print("Unknown command\n")
            help_message()
    else:
        help_message()
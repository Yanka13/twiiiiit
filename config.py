import os


class Config(object):
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if 'RDS_DB_NAME' in os.environ:
        SQLALCHEMY_DATABASE_URI = \
            'postgresql://{username}:{password}@{host}:{port}/{database}'.format(
            username=os.environ['RDS_USERNAME'],
            password=os.environ['RDS_PASSWORD'],
            host=os.environ['RDS_HOSTNAME'],
            port=os.environ['RDS_PORT'],
            database=os.environ['RDS_DB_NAME'],
        )
    else:
        SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']



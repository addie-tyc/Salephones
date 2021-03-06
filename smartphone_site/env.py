from dotenv import load_dotenv

import os

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY')
SQL_HOST = os.getenv('SQL_HOST')
SQL_USER = os.getenv('SQL_USER')
SQL_PWD = os.getenv('SQL_PWD')

MONGO_HOST = os.getenv('MONGO_HOST')
MONGO_USER = os.getenv('MONGO_USER')
MONGO_PWD = os.getenv('MONGO_PWD')

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_KEY")

SSL_PATH = os.getenv("SSL_PATH")
SSL_FILE = os.getenv("SSL_FILE")
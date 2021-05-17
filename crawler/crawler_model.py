from dotenv import load_dotenv
from flask import request, make_response
import pymysql
import jwt

import pytz
from datetime import datetime, timedelta
import os

load_dotenv()

USER = os.getenv("SQL_USER")
PWD = os.getenv("SQL_PSW")
HOST = os.getenv("SQL_HOST")

class Ptt():

    def __init__(self):
        self.db = pymysql.connect(host=HOST, user=USER, password=PWD, database="smartphone")

    def insert_post(self, raw_data, data):
        db = self.db
        db.ping()
        cursor = db.cursor()
        cursor.executemany('''
                           INSERT INTO raw_ptt
                           (`link`, `html_body`)
                           VALUES (%s, %s)
                           ''', raw_data)
        cursor.executemany('''
                           INSERT INTO ptt
                           (`title`, `storage`, `price`, `new`, `sold`, 
                           `account`, `box`, `link`, `created_at`, `page_number`,
                           `source`)
                           VALUES (%s, %s, %s, %s, %s,
                                   %s, %s, %s, %s, %s,
                                   %s)
                           ''', data)
        db.commit()
        db.close()

    def select_max_page_number(self, source):
        db = self.db
        cursor = db.cursor(pymysql.cursors.DictCursor)
        cursor.execute('''
                       SELECT MAX(page_number) AS max_page FROM ptt
                        WHERE source = %s
                       ''', source)
        result = cursor.fetchone()
        max_page = result["max_page"]
        db.close()
        return max_page

class Landtop():

    def __init__(self):
        self.db = pymysql.connect(host=HOST, user=USER, password=PWD, database="smartphone")

    def insert_landtop_phones(self, data):
        db = self.db
        db.ping()
        cursor = db.cursor()
        cursor.executemany('''
                           INSERT INTO landtop
                           (`title`, `storage`, `price`, `created_at`)
                           VALUES (%s, %s, %s, %s)
                           ''', data)
        db.commit()
        db.close()      
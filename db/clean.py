import os
import sys
import json
from ConfigParser import ConfigParser
from pymongo import MongoClient

CONFIG = ConfigParser()

CONFIG_CONFIRMATION_LOCALE = 'Will read configuration from this file: {}'
DB_CONNECTED = 'Connection to database established...'
DB_DETAIL_LOCALE = 'Host: {}\nPort: {}\nDatabase: {}'
DB_CLEAN_CONFIRMATION = '{} database has been dropped from MongoDB server'

def read_config(file_name):
  print CONFIG_CONFIRMATION_LOCALE.format(file_name)
  CONFIG.read(file_name)

def connect_to_db():
  host = CONFIG.get('DB', 'Host')
  port = CONFIG.get('DB', 'Port')
  db = CONFIG.get('DB', 'Database')
  collection = CONFIG.get('DB', 'Collection')
  url = 'mongodb://{}:{}'.format(host, port, db)
  collection_socket = MongoClient(url)
  print DB_CONNECTED
  print
  print DB_DETAIL_LOCALE.format(host, port, db)
  return collection_socket

def clean(db):
  db_name = CONFIG.get('DB', 'Database')
  db.drop_database(db_name)
  print DB_CLEAN_CONFIRMATION.format(db_name.upper())

def main(argv):
  read_config(argv[1])
  print
  db = connect_to_db()
  print
  clean(db)
  print

if __name__ == '__main__':
  main(sys.argv)

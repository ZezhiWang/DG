import os
import sys
import json
from ConfigParser import ConfigParser
from pymongo import MongoClient

CONFIG = ConfigParser()

PROGRESS_STEP = 50
PROGRESS_BLOCK = 100 / PROGRESS_STEP

CONFIG_CONFIRMATION_LOCALE = 'Will read configuration from this file: {}'
DIRECTORY_CONFIRMATION_LOCALE = 'Will read raw data from this directory: {}'
INITIATION = 'Traing data loading initiated...'
DB_CONNECTED = 'Connection to database established...'
DB_DETAIL_LOCALE = 'Host: {}\nPort: {}\nDatabase: {}\nCollection: {}'
DB_URL_LOCALE = 'mongodb://{}:{}'
CATAGORY_DETAIL_LOCALE = '{} catagories: {}'
READ_START_LOCAL = 'Reading data from file: {}'
READ_PROGRESS_BAR_LOCALE = '\rLoading progress: [{}] {}%'
COMPLETION = 'Traing data loading completed.'
STATISTICS = '{} records stored in total'

def read_config(file_name):
  print CONFIG_CONFIRMATION_LOCALE.format(file_name)
  CONFIG.read(file_name)

def connect_to_db():
  host = CONFIG.get('DB', 'Host')
  port = CONFIG.get('DB', 'Port')
  db = CONFIG.get('DB', 'Database')
  collection = CONFIG.get('DB', 'Collection')
  url = DB_URL_LOCALE.format(host, port)
  collection_socket = MongoClient(url)[db][collection]
  print DB_CONNECTED
  print
  print DB_DETAIL_LOCALE.format(host, port, db, collection)
  return collection_socket

def locate_source_file(directory):
  return [directory + file_name for file_name in os.listdir(directory)
                                if file_name.endswith('.ndjson')]

def file_size(file_name):
  with open(file_name, 'r') as doc:
    return sum(1 for _ in doc)

def show_progress(progress):
  bar = progress * '=' + '>' + (PROGRESS_STEP - progress) * ' '
  line = READ_PROGRESS_BAR_LOCALE.format(bar, progress * PROGRESS_BLOCK)
  sys.stdout.write(line)
  sys.stdout.flush()

def pack(drawing):
  for i, stroke in enumerate(drawing):
    drawing[i] = '|'.join(str(a) + '|' + str(b) for a, b in zip(*stroke))
  return '-'.join(drawing)

def store_object(line, collection):
  obj = json.loads(line.strip())
  obj['_id'] = obj['key_id']
  del obj['timestamp']
  del obj['key_id']
  obj['drawing'] = pack(obj['drawing'])
  try:
    collection.insert_one(obj)
  except Exception:
    pass

def get_catagory(file_name):
  file_name = file_name.split('/')[-1]
  return os.path.splitext(file_name)[0].capitalize()

def store_file(file_name, collection):
  with open(file_name, 'r') as doc:
    print READ_START_LOCAL.format(get_catagory(file_name))
    completed, progress, total = 0, 0, file_size(file_name)
    show_progress(progress)
    for line in doc:
      store_object(line, collection)
      completed += PROGRESS_STEP
      if completed / total != progress:
        progress += 1
        show_progress(progress)
  print

def main(argv):
  read_config(argv[1])
  print
  data_directory = CONFIG.get('SOURCE', 'Directory')
  source_file_list = locate_source_file(data_directory)
  catagory_count = len(source_file_list)
  object_total = sum(file_size(file_name) for file_name in source_file_list)
  catagories = ', '.join([get_catagory(file_name) for file_name in source_file_list])
  collection = connect_to_db()

  print
  print DIRECTORY_CONFIRMATION_LOCALE.format(data_directory)
  print
  print INITIATION
  print
  print CATAGORY_DETAIL_LOCALE.format(catagory_count, catagories)
  print
  for file_name in source_file_list:
    store_file(file_name, collection)
    print
  print COMPLETION
  print STATISTICS.format(object_total)
  print

if __name__ == '__main__':
  main(sys.argv)

from pymongo import MongoClient
from bson.objectid import ObjectId

DB_URL_LOCALE = 'mongodb://{}:{}'

class Driver:
  def __init__(self, host='172.17.0.1', port=27017, 
                     db='dg', collection='sketch'):
    url = DB_URL_LOCALE.format(host, port)
    self.__collection = MongoClient(url)[db][collection]
    self.__cache = {}

  def __cached(function):
    def cached_function(*argv, **kw):
      cache = argv[0].__cache
      token = tuple([function.__name__] + list(argv[1:]))
      if token not in cache:
        cache[token] = function(*argv, **kw)
      return cache[token]
    return cached_function

  @__cached
  def total_size(self):
    return self.__collection.find().count()

  @__cached
  def catagory_list(self):
    return self.__collection.distinct('word')

  @__cached
  def size_of_catagory(self, catagory):
    return self.__collection.find({ 'word': catagory }).count()

  @__cached
  def find_by_id(self, object_id):
    return self.__collection.find_one({ '_id': ObjectId(object_id) })

  def find_by_catagory(self, catagory):
    return self.__collection.find({ 'word': catagory })

  def find_all(self):
    return self.__collection.aggregate([{'$sample': {'size': self.__collection.count()}}], allowDiskUse=True)
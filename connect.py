import psycopg2
from config import config

def connect():
  con = None
  try:
    params = config()
    # print('Connecting to PostgreSQL database')
    con = psycopg2.connect(**params)
    
    return con

  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  
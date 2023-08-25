from connect import connect

if __name__ == '__main__':
  con = connect()
  cur = con.cursor()
  print('The current user is:')
  query = ('SELECT id FROM users WHERE id = %s')
  query = 'SELECT taskid, task, description, to_char(debut::timestamp, \'dd-mm-yyyy hh:mi\'), CASE WHEN fin <> \'En cours...\' THEN to_char(fin::timestamp, \'dd-mm-yyyy hh:mi\') ELSE fin END FROM tasks WHERE userid = %s ORDER BY debut'
  id = (1,)
  cur.execute(query, id)
  db_result = cur.fetchall()
  
  print(db_result)
  # for row in db_result:
  #   print(row)
  myiti = iter(db_result)
  a = next(myiti)
  print(a)
  print(cur.rowcount)
  cur.close()
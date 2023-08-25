from connect import connect

user_id = None

def home():
  print('\t1. Se connecter')
  print('\t2. Créer un utilisateur')

  try:
    res = int(input('\nEntrer une réponse: '))
  except:
    print('\n!!! Entrer un entier !!!\n')
    return home()

  if res == 1:
    user_id = login()
  elif res == 2:
    user_id = signup()
  else:
    print('\n!!! Entrer parmis les suggestions !!!\n')
    return home()
  return user_id

def signup():
  con = connect()
  cur = con.cursor()
  name = str(input('\tEntrer le nom: '))
  name = name.strip()
  pseudo = True
  tente = 3
  while pseudo:
    if tente > 0:
      id = str(input('\tEntrer le pseudo: '))
      id = id.strip()
      query = ('SELECT * FROM users WHERE identifiant = %s')
      cur.execute(query, (id,))
      cur.fetchone()

      if cur.rowcount > 0:
        print('\n!!! Ce pseudo existe déjà !!!\n')
        tente = tente - 1
        pseudo = True
      else:
        pseudo = False
    else :
      pseudo = False
      return home()
  passwd1 = str(input('\tEntrer le mot de passe: '))
  passwd1 = passwd1.strip()
  passwd = True
  tente = 2
  while passwd:
    if tente > 0:
      passwd2 = str(input('\tResaisir le mot de passe: '))
      passwd2 = passwd2.strip()
      if passwd1 == passwd2:
        query = ('INSERT INTO users(name, identifiant, password) VALUES (%s, %s, md5(%s)) RETURNING userid')
        cur.execute(query, (name, id, passwd1))
        query_result = cur.fetchone()
        con.commit()
        user_iter = iter(query_result)
        user_id = next(user_iter)
        return user_id
      else:
        print('\n!!! Mot de passe différent !!!\n')
        tente = tente - 1
    else:
      passwd = False
      print('!!! Réessayer la création de l\'utilisateur !!!\n')
      return signup()

def login():
  con = connect()
  cur = con.cursor()
  id = str(input('\n\tEntrer l\'identifiant: '))
  id = id.strip()
  passwd = str(input('\tEntrer le mot de passe: '))
  passwd = passwd.strip()

  query = ('SELECT userid FROM users WHERE identifiant = %s AND password = md5(%s)')
  cur.execute(query, (id, passwd))
  query_result = cur.fetchone()
  
  if cur.rowcount > 0:
    user_iter = iter(query_result)
    return next(user_iter)
  else:
    query = ('SELECT * FROM users WHERE identifiant = %s')
    cur.execute(query, (id,))
    
    if cur.rowcount == 0:
      print('\n!!! Identifiant inexistant !!!')
      return login()
    else:
      print('\n!!! Mot de passe incorrect !!!')
      return login()

  

def actions(user_id):
  print('\n\n**************** Bienvenu ********************\n')
  print('\nVoici les actions vous pouvez faire:\n')
  print('\t1. Ajouter une tâche')
  print('\t2. Lister les tâches')
  print('\t3. Historiques')
  print('\t4. Rechercher des tâches')

  try:
    choix = int(input('Choisir une action: '))
  except:
    print('!!! Entrer un entier !!!')
    return actions(user_id)

  if choix == 1:
    return add(user_id)
  elif choix == 2:
    return show(user_id)
  elif choix == 3:
    return history(user_id)
  elif choix == 4:
    print('\n------Recherche des tâches-----\n')
    return search(user_id)
  else :
    return actions(user_id)

def add(user_id):
  print('\n------Ajout d\'une tâche-----\n')
  con = connect()
  cur = con.cursor()
  task = str(input('Entrer le titre de tâche: '))
  task = task.strip()
  description = str(input('Entrer la description: '))
  description = description.strip()
  description = description.capitalize()
  query = 'INSERT INTO tasks (userid, task, description) VALUES (%s, INITCAP(%s), %s) RETURNING taskid'
  cur.execute(query, (user_id, task, description))
  query_result = cur.fetchone()
  con.commit()
  if cur.rowcount > 0:
    return show(user_id)

def show(user_id):
  print('\n-------Liste des tâches-------\n')
  con = connect()
  cur = con.cursor()
  query = 'SELECT taskid, task, description, to_char(debut::timestamp, \'dd-mm-yyyy à hh24:mi\'), CASE WHEN fin <> \'En cours...\' THEN to_char(fin::timestamp, \'dd-mm-yyyy à hh24:mi\') ELSE fin END FROM tasks WHERE userid = %s ORDER BY debut'
  cur.execute(query, (user_id,))
  query_result = cur.fetchall()
  if cur.rowcount == 0:
    print('\n!!! Aucune tâche, entrer une nouvelle tâche !!!')
    return add(user_id)
  else:
    for row in query_result:
      print('#' + str(row[0]) + '\nTitre: ' + row[1] + '  Début: ' + row[3] + '\nDescription: ' + row[2] + '\nFin: ' + row[4] + '\n')

    print('\n-----Editer les tâches------\n')
    print('\t1. Terminer une tâche')
    print('\t2. Modifier une tâche')
    print('\n\t0. Menu principal')
    print('\t9. Quitter')

    try:
      res = int(input('\nEntrer une réponse: '))
    except: 
      print('!!! Entrer un nombre entier !!!')
      return show(user_id)
    
    if res == 1:
      return finish(user_id)
    elif res == 2:
      return edit(user_id)
    elif res == 0:
      return actions(user_id)
    elif res == 9:
      print('\n\tA bientôt!')
      return exit()
    else:
      print('!!! Entrer parmi les suggestions !!!')
      return show(user_id)

def finish(user_id):
  print('\n--------Terminer une tâche-----------')
  try:
    task_id = int(input('\tEntrer le numéro de tâche: '))
  except:
    print('!!!Entrer un nombre entier!!!')
    return finish(user_id)

  con = connect()
  cur = con.cursor()
  query = 'SELECT taskid FROM tasks WHERE userid = %s AND taskid = %s'
  cur.execute(query, (user_id, task_id,))
  query_result = cur.fetchone()
  if cur.rowcount == 0:
    print('\n!!! Numéro de tâche introuvable !!!')
    return finish(user_id)
  else:
    query = 'SELECT taskid FROM tasks WHERE userid = %s AND taskid = %s AND fin = \'En cours...\''
    cur.execute(query, (user_id, task_id,))
    query_result = cur.fetchone()
    if cur.rowcount == 0:
      print('\n!!! Cette tâche est déjà terminée!!!')
      return actions(user_id)
    else:
      query = 'UPDATE tasks SET fin = now() WHERE userid = %s AND taskid = %s'
      cur.execute(query, (user_id, task_id))
      con.commit()
      return show(user_id)


def edit(user_id):
  print('\n----- Modification d\'une tâche ---------\n')
  con = connect()
  cur = con.cursor()
  try:
    task_id = int(input('\tEntrer le numéro de tâche: '))
  except:
    print('!!!Entrer un nombre entier!!!')
    return edit(user_id)
  query = 'SELECT taskid FROM tasks WHERE userid = %s AND taskid = %s'
  cur.execute(query, (user_id, task_id,))
  query_result = cur.fetchone()
  if cur.rowcount == 0:
    print('\n!!! Numéro de tâche introuvable !!!')
    return edit(user_id)
  else:
    query = 'SELECT taskid FROM tasks WHERE userid = %s AND taskid = %s AND fin = \'En cours...\''
    cur.execute(query, (user_id, task_id,))
    query_result = cur.fetchone()
    if cur.rowcount == 0:
      print('\n!!! Cette tâche est déjà terminée, Impossible à modifier !!!')
      return show(user_id)
    else:
      task = str(input('Entrer le titre de tâche: '))
      task = task.strip()
      description = str(input('Entrer la description: '))
      description = description.strip()
      description = description.capitalize()

      query = 'UPDATE tasks SET task = %s, description = %s WHERE userid = %s AND taskid = %s'
      cur.execute(query, (task, description, user_id, task_id,))
      con.commit()
      return show(user_id)
  
def search(user_id):
  print('------ Rechercher une tâche --------')
  con = connect()
  cur = con.cursor()
  task = str(input('Entrer une tâche ou un état ou une date(dd-mm-yyyy): '))
  task = task.strip()
  query = "SELECT taskid, task, description, to_char(debut::timestamp, \'dd-mm-yyyy à hh24:mi\'), CASE WHEN fin <> \'En cours...\' THEN to_char(fin::timestamp, \'dd-mm-yyyy à hh24:mi\') ELSE fin END FROM tasks WHERE userid = "+str(user_id)+" AND task ILIKE '%"+task+"%' OR fin ILIKE '%"+task+"%' OR to_char(debut::timestamp, 'dd-mm-yyyy') ILIKE '%"+task+"%' ORDER BY debut"
  # query=("SELECT * FROM tasks WHERE  task ilike '%"+task+"%' or fin ~~* '%"+task+"%' or debut ~~*  '%"+task+"%'")
  cur.execute(query)
  query_result = cur.fetchall()
  print('\n')
  for row in query_result:
    print('#' + str(row[0]) + '\nTitre: ' + row[1] + '  Début: ' + row[3] + '\nDescription: ' + row[2] + '\nFin: ' + row[4] + '\n')
  # print(query_result)
  print('\n\t0. Menu principal')
  print('\t9. Quitter')

  try:
    res = int(input('\nEntrer une réponse: '))
  except: 
    print('!!! Entrer un nombre entier !!!')
  
  if res == 9:
    print('\n\tA bientôt!')
    return exit()
  else:
    return actions(user_id)  

def history(user_id):
  print('\n------ Historiques des tâches ---------')
  con = connect()
  cur = con.cursor()
  query = "SELECT taskid, task, description, to_char(fin::timestamptz - debut::timestamptz, 'hh24 heure(s) mi') || ' minute(s)' FROM tasks WHERE userid = %s AND fin <> 'En cours...'"
  cur.execute(query, (user_id,))
  query_result = cur.fetchall()

  if cur.rowcount == 0:
    print('\n!!! Aucune historique !!!')
    return actions(user_id)
  else:
    for row in query_result:
      print('#' + str(row[0]) +'\nTitre: '+ row[1] + '\nDescription: ' + row[2] + '\nDurée: ' + row[3] + '\n')

    print('\n-----Editer les historiques------\n')
    print('\t1. Effacer une historique')
    print('\n\t0. Menu principal')
    print('\t9. Quitter')

    try:
      res = int(input('\nEntrer une réponse: '))
    except: 
      print('!!! Entrer un nombre entier !!!')
    
    if res == 1:
      return remove(user_id)
    elif res == 9:
      print('\n\tA bientôt!')
      return exit()
    else:
      return actions(user_id)


def remove(user_id):
  print('\n----- Suppression d\'une historique ---------\n')
  con = connect()
  cur = con.cursor()
  try:
    task_id = int(input('\tEntrer le numéro de tâche: '))
  except:
    print('!!!Entrer un nombre entier!!!')
    return history(user_id)
  query = 'SELECT taskid FROM tasks WHERE userid = %s AND taskid = %s AND fin <> \'En cours...\''
  cur.execute(query, (user_id, task_id,))
  query_result = cur.fetchone()
  if cur.rowcount == 0:
    print('\n!!! Numéro de tâche introuvable !!!')
    return history(user_id)
  else:
    query = 'DELETE FROM tasks WHERE userid = %s AND taskid = %s AND fin <> \'En cours...\''
    cur.execute(query, (user_id, task_id,))
    con.commit()
    return history(user_id)
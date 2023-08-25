from features import home, actions

user_id = None

if __name__ == '__main__':
  print('\n************** Gestion de tâches personnelles ***************\n')
  user_id = home()
  action = actions(user_id)
  # action = actions()
  #  choice(action)
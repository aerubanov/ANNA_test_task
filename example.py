import requests
import json
import datetime

username = 'user1'
password = 'qwerty'
host = 'http://localhost:8080'

if __name__ == '__main__':
    # registration and authorization
    requests.post(host + '/registration', json={'username': username, 'password': password})
    resp = requests.post(host + '/login', json={'username': username, 'password': password})
    data = json.loads(resp.text)
    token = data['token']

    # add tasks
    requests.post(host + '/task',
                  headers={'Authorization': f'Basic {token}'},
                  json={
                      'name': 'task 1',
                      'description': 'description 1',
                      'status': 'Новая',
                      'end_date': str(datetime.datetime(2020, 10, 3)),
                  })
    resp = requests.post(host + '/task',
                         headers={'Authorization': f'Basic {token}'},
                         json={
                             'name': 'task 2',
                             'description': 'description 2',
                             'status': 'Новая',
                             'end_date': str(datetime.datetime(2020, 10, 3)),
                         })
    data = json.loads(resp.text)
    task_id = data['task_id']

    # get tasks
    resp = requests.get(host+'/tasks', headers={'Authorization': f'Basic {token}'}, json={})
    print(json.loads(resp.text))

    # change task
    requests.put(host+'/task',
                        headers={'Authorization': f'Basic {token}'},
                        json={
                            'task_id': task_id,
                            'new_status': 'В работе',
                        })
    resp = requests.get(host+'/tasks',
                        headers={'Authorization': f'Basic {token}'},
                        json={'filter_by_status': 'В работе'})
    print(json.loads(resp.text))

    # get task changes
    resp = requests.get(host+'/task_changes', headers={'Authorization': f'Basic {token}'}, json={'task_id': task_id})
    print(json.loads(resp.text))

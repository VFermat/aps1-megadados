from fastapi.testclient import TestClient 
from main import app
from pydantic import UUID1
from random import randint

client = TestClient(app)

def test_read_main_returns_not_found():
    response = client.get('/')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}

def test_read_healthcheck_returns_ok():
    response = client.get('/test')
    assert response.status_code == 200
    assert response.json() == {'message': 'all good'}

def test_read_task_returns_ok():
    response = client.post(
        '/task',
        json={
            "title": "Random task title",
            "description": "Random task description"
        }
    )
    assert response.status_code == 201
    task = response.json()
    tasks_returned = client.get('/task')
    tasks_returned = tasks_returned.json()
    assert len(tasks_returned) == 1
    assert task == tasks_returned[0]

def test_read_multiple_tasks_returns_ok():
    tasks = []
    for i in range(randint(1, 10)):
        response = client.post(
            '/task',
            json={
                "title": "Random task title",
                "description": "Random task description"
            }
        )
        assert response.status_code == 201
        tasks.append(response.json())
    tasks_returned = client.get('/task')
    tasks_returned = tasks_returned.json()
    assert len(tasks_returned) == len(tasks) + 1
    for task in tasks:
        assert task in tasks_returned

def test_read_specific_task_returns_ok():
    response = client.post(
        '/task',
        json={
            "title": "Random task title",
            "description": "Random task description"
        }
    )
    assert response.status_code == 201
    task = response.json()
    task_id = task['uuid']
    response = client.get(f'/task/{task_id}')
    tasks_returned = response.json()
    assert response.status_code == 200
    assert tasks_returned == task

def test_read_task_returns_not_found():
    response = client.get(
        '/task/e4782a82-f38e-11ea-85fc-acde48001122'
    )
    assert response.status_code == 404
    assert response.json() == {'message': 'Task not found'}

def test_read_task_returns_wrong_path():
    response = client.get(
        '/task/1'
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['path', 'task_id'], 'msg': 'value is not a valid uuid', 'type': 'type_error.uuid'}]}

def test_write_task_returns_ok():
    response = client.post(
        '/task',
        json={
            "title": "Random task title",
            "description": "Random task description"
        }
    )
    assert response.status_code == 201
    response = response.json()
    assert response['uuid']
    assert response['status'] == 'todo'
    assert response['title'] == 'Random task title'
    assert response['description'] == 'Random task description'

def test_delete_task_returns_ok():
    response = client.post(
        '/task',
        json={
            "title": "Random task title",
            "description": "Random task description"
        }
    )
    assert response.status_code == 201
    uuid = response.json()['uuid']
    response = client.delete(
        f'/task/{uuid}'
    )
    assert response.status_code == 204

def test_delete_task_returns_not_found():
    response = client.delete(
        '/task/e4782a82-f38e-11ea-85fc-acde48001122'
    )
    assert response.status_code == 404
    assert response.json() == {'message': 'Task not found'}

def test_delete_task_returns_wrong_path():
    response = client.delete(
        '/task/1'
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': ['path', 'task_id'], 'msg': 'value is not a valid uuid', 'type': 'type_error.uuid'}]}


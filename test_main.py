from random import randint

from fastapi.testclient import TestClient
from pydantic import UUID1

from main import app

client = TestClient(app)


def test_read_main_returns_not_found():
    response = client.get('/')
    assert response.status_code == 404
    assert response.json() == {'detail': 'Not Found'}


def test_read_healthcheck_returns_ok():
    response = client.get('/test')
    assert response.status_code == 200
    assert response.json() == {'message': 'all good'}

def test_read_tasks_returns_ok():
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
    assert len(tasks_returned) == len(tasks)
    for task in tasks:
        assert task in tasks_returned

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
    assert response.json() == {'detail': [{'loc': [
        'path', 'task_id'], 'msg': 'value is not a valid uuid', 'type': 'type_error.uuid'}]}


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
    assert response.json() == {'detail': [{'loc': [
        'path', 'task_id'], 'msg': 'value is not a valid uuid', 'type': 'type_error.uuid'}]}


def test_patch_task_title_returns_ok():
    task = {
        "title": "Random task title",
        "description": "Random task description"
    }
    response = client.post(
        '/task',
        json=task
    )
    assert response.status_code == 201
    task = response.json()
    uuid = response.json()['uuid']
    response = client.patch(
        f'/task/{uuid}',
        json={
            'title': 'New Title'
        }
    )
    modified_task = response.json()
    assert response.status_code == 200
    assert modified_task['title'] == 'New Title'
    assert modified_task['description'] == task['description']
    assert modified_task['status'] == task['status']


def test_patch_task_description_returns_ok():
    task = {
        "title": "Random task title",
        "description": "Random task description"
    }
    response = client.post(
        '/task',
        json=task
    )
    assert response.status_code == 201
    task = response.json()
    uuid = response.json()['uuid']
    response = client.patch(
        f'/task/{uuid}',
        json={
            'description': 'New Description'
        }
    )
    modified_task = response.json()
    assert response.status_code == 200
    assert modified_task['description'] == 'New Description'
    assert modified_task['title'] == task['title']
    assert modified_task['status'] == task['status']


def test_patch_task_status_returns_ok():
    task = {
        "title": "Random task title",
        "description": "Random task description"
    }
    response = client.post(
        '/task',
        json=task
    )
    assert response.status_code == 201
    uuid = response.json()['uuid']
    response = client.patch(
        f'/task/{uuid}',
        json={
            'status': 'doing'
        }
    )
    modified_task = response.json()
    assert response.status_code == 200
    assert modified_task['description'] == task['description']
    assert modified_task['title'] == task['title']
    assert modified_task['status'] == "doing"


def test_patch_task_status_returns_invalid_type():
    task = {
        "title": "Random task title",
        "description": "Random task description"
    }
    response = client.post(
        '/task',
        json=task
    )
    assert response.status_code == 201
    uuid = response.json()['uuid']
    response = client.patch(
        f'/task/{uuid}',
        json={
            'status': 'random'
        }
    )
    modified_task = response.json()
    print(modified_task)
    assert response.status_code == 422
    assert modified_task == {'detail': [{'loc': ['body', 'status'], 'msg': "value is not a valid enumeration member; permitted: 'todo', 'doing', 'done'", 'type': 'type_error.enum', 'ctx': {'enum_values': ['todo', 'doing', 'done']}}]}


def test_patch_task_returns_not_found():
    response = client.patch(
        '/task/e4782a82-f38e-11ea-85fc-acde48001122', json={}
    )
    print(response.text)
    assert response.status_code == 404
    assert response.json() == {'message': 'Task not found'}


def test_patch_task_returns_wrong_path():
    response = client.patch(
        '/task/1', json={}
    )
    assert response.status_code == 422
    assert response.json() == {'detail': [{'loc': [
        'path', 'task_id'], 'msg': 'value is not a valid uuid', 'type': 'type_error.uuid'}]}

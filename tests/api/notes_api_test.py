import json
# import os
import requests
from faker import Faker
import time
from .support_api import create_note_api, create_user_api, delete_json_file, delete_note_api, delete_user_api, login_user_api

def test_create_note_api():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_id = data['user_id']
    user_token = data['user_token']
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_description = Faker().sentence(3)
    note_title = Faker().sentence(2)
    body = {'category': note_category, 'description': note_description, 'title': note_title}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    resp = requests.post("https://practice.expandtesting.com/notes/api/notes", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Note successfully created" == respJS['message']
    assert note_category == respJS['data']['category']
    assert note_description == respJS['data']['description']
    assert note_title == respJS['data']['title']
    assert user_id == respJS['data']['user_id']
    note_id = respJS['data']['id']
    note_created_at = respJS['data']['created_at']
    note_completed = respJS['data']['completed']
    note_updated_at = respJS['data']['updated_at']
    combined_responses = {
        'note_category': note_category,
        'note_completed': note_completed,
        'note_description': note_description,
        'note_title': note_title,
        'note_id': note_id,
        'note_created_at': note_created_at,
        'note_updated_at': note_updated_at,
        'user_id': user_id,
        'user_token': user_token
    }
    with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
        json.dump(combined_responses, json_file, indent=4)
    # This functions is here only for practice purpose since we already have delete_user_api to delete the user right away.
    delete_note_api(randomData)
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_create_note_api_bad_request():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_id = data['user_id']
    user_token = data['user_token']
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_description = Faker().sentence(3)
    note_title = Faker().sentence(2)
    body = {'category': 'a', 'description': note_description, 'title': note_title}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    resp = requests.post("https://practice.expandtesting.com/notes/api/notes", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "Category must be one of the categories: Home, Work, Personal" == respJS['message']
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_create_note_api_unauthorized():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_id = data['user_id']
    user_token = data['user_token']
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_description = Faker().sentence(3)
    note_title = Faker().sentence(2)
    body = {'category': note_category, 'description': note_description, 'title': note_title}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': '@'+user_token}
    resp = requests.post("https://practice.expandtesting.com/notes/api/notes", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message']
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_get_notes_api():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_id = data['user_id']
    user_token = data['user_token']
    note_category_array = [Faker().random_element(elements=('Home', 'Personal', 'Work')), 'Home', 'Personal', 'Work']
    note_created_at_array = ["a", "b", "c", "d"]
    note_completed_array = [False, False, False, True]
    note_id_array = ["a", "b", "c", "d"]
    note_updated_at_array = ["a", "b", "c", "d"]
    note_description_array = [Faker().sentence(3), Faker().sentence(3), Faker().sentence(3), Faker().sentence(3)]
    note_title_array = [Faker().sentence(2), Faker().sentence(2), Faker().sentence(2), Faker().sentence(2)]
    # creates 4 notes, set the last as "complete" and asserts the 4 objects in the response.
    for x in range(4):
        body = {'category': note_category_array[x], 'description': note_description_array[x], 'title': note_title_array[x]}
        print(body)
        headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
        resp = requests.post("https://practice.expandtesting.com/notes/api/notes", headers=headers, data=body)
        respJS = resp.json()
        print(respJS)
        assert True == respJS['success']
        assert 200 == respJS['status']
        assert "Note successfully created" == respJS['message']
        assert note_category_array[x] == respJS['data']['category']
        assert note_description_array[x] == respJS['data']['description']
        assert note_title_array[x] == respJS['data']['title']        
        note_id_array[x] = respJS['data']['id']
        note_created_at_array[x] = respJS['data']['created_at']
        note_updated_at_array[x] = respJS['data']['updated_at']
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    body = {'completed': "true"}
    print(body)
    resp = requests.patch(f"https://practice.expandtesting.com/notes/api/notes/{note_id_array[3]}", headers=headers, data=body)
    respJS = resp.json()
    note_updated_at_array[3] = respJS['data']['updated_at']    
    headers = {'accept': 'application/json', 'x-auth-token': user_token}
    resp = requests.get(f"https://practice.expandtesting.com/notes/api/notes", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Notes successfully retrieved" == respJS['message']
    for x in range(4):
        assert note_category_array[x] == respJS['data'][3-x]['category']
        assert note_created_at_array[x] == respJS['data'][3-x]['created_at']
        assert note_completed_array[x] == respJS['data'][3-x]['completed']
        assert note_description_array[x] == respJS['data'][3-x]['description']
        assert note_id_array[x] == respJS['data'][3-x]['id']
        assert note_title_array[x] == respJS['data'][3-x]['title']
        assert note_updated_at_array[x] == respJS['data'][3-x]['updated_at']
        assert user_id == respJS['data'][3-x]['user_id']        
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_get_notes_api_unauthorized():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_id = data['user_id']
    user_token = data['user_token']
    note_category_array = [Faker().random_element(elements=('Home', 'Personal', 'Work')), 'Home', 'Personal', 'Work']
    note_created_at_array = ["a", "b", "c", "d"]
    note_completed_array = [False, False, False, True]
    note_id_array = ["a", "b", "c", "d"]
    note_updated_at_array = ["a", "b", "c", "d"]
    note_description_array = [Faker().sentence(3), Faker().sentence(3), Faker().sentence(3), Faker().sentence(3)]
    note_title_array = [Faker().sentence(2), Faker().sentence(2), Faker().sentence(2), Faker().sentence(2)]
    # creates 4 notes, set the last as "complete" and asserts the 4 objects in the response.
    for x in range(4):
        body = {'category': note_category_array[x], 'description': note_description_array[x], 'title': note_title_array[x]}
        print(body)
        headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
        resp = requests.post("https://practice.expandtesting.com/notes/api/notes", headers=headers, data=body)
        respJS = resp.json()
        print(respJS)
        assert True == respJS['success']
        assert 200 == respJS['status']
        assert "Note successfully created" == respJS['message']
        assert note_category_array[x] == respJS['data']['category']
        assert note_description_array[x] == respJS['data']['description']
        assert note_title_array[x] == respJS['data']['title']        
        note_id_array[x] = respJS['data']['id']
        note_created_at_array[x] = respJS['data']['created_at']
        note_updated_at_array[x] = respJS['data']['updated_at']
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    body = {'completed': "true"}
    print(body)
    resp = requests.patch(f"https://practice.expandtesting.com/notes/api/notes/{note_id_array[3]}", headers=headers, data=body)
    respJS = resp.json()
    note_updated_at_array[3] = respJS['data']['updated_at']    
    headers = {'accept': 'application/json', 'x-auth-token': '@'+user_token}
    resp = requests.get(f"https://practice.expandtesting.com/notes/api/notes", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message']      
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_get_note_api():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_category = data['note_category']
    note_created_at = data['note_created_at']
    note_completed = data['note_completed']
    note_description = data['note_description']
    note_id = data['note_id']
    note_title = data['note_title']
    note_updated_at = data['note_updated_at']
    user_id = data['user_id']
    user_token = data['user_token']
    headers = {'accept': 'application/json', 'x-auth-token': user_token}
    resp = requests.get(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Note successfully retrieved" == respJS['message']
    assert note_category == respJS['data']['category']
    assert note_created_at == respJS['data']['created_at']
    assert note_completed == respJS['data']['completed']
    assert note_description == respJS['data']['description']
    assert note_id == respJS['data']['id']
    assert note_title == respJS['data']['title']
    assert note_updated_at == respJS['data']['updated_at']
    assert user_id == respJS['data']['user_id']
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_get_note_api_unauthorized():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_category = data['note_category']
    note_created_at = data['note_created_at']
    note_completed = data['note_completed']
    note_description = data['note_description']
    note_id = data['note_id']
    note_title = data['note_title']
    note_updated_at = data['note_updated_at']
    user_id = data['user_id']
    user_token = data['user_token']
    headers = {'accept': 'application/json', 'x-auth-token': '@'+user_token}
    resp = requests.get(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message'] 
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_api():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_created_at = data['note_created_at']
    note_completed = True
    note_description = Faker().sentence(3)
    note_id = data['note_id']
    note_title = Faker().sentence(2)
    user_id = data['user_id']
    user_token = data['user_token']    
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    body = {'category': note_category, 'completed': "true", 'description': note_description, 'title': note_title}
    print(body)
    resp = requests.put(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Note successfully Updated" == respJS['message']
    assert note_category == respJS['data']['category']
    assert note_created_at == respJS['data']['created_at']
    assert note_completed == respJS['data']['completed']
    assert note_description == respJS['data']['description']
    assert note_id == respJS['data']['id']
    assert note_title == respJS['data']['title']
    assert user_id == respJS['data']['user_id']
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_api_bad_request():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_created_at = data['note_created_at']
    note_completed = True
    note_description = Faker().sentence(3)
    note_id = data['note_id']
    note_title = Faker().sentence(2)
    user_id = data['user_id']
    user_token = data['user_token']    
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    body = {'category': 'a', 'completed': "true", 'description': note_description, 'title': note_title}
    print(body)
    resp = requests.put(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "Category must be one of the categories: Home, Work, Personal" == respJS['message']
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_api_unauthorized():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_created_at = data['note_created_at']
    note_completed = True
    note_description = Faker().sentence(3)
    note_id = data['note_id']
    note_title = Faker().sentence(2)
    user_id = data['user_id']
    user_token = data['user_token']    
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': "@"+user_token}
    body = {'category': note_category, 'completed': "true", 'description': note_description, 'title': note_title}
    print(body)
    resp = requests.put(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message'] 
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_status_api():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_category = data['note_category']
    note_created_at = data['note_created_at']
    note_description = data['note_description']
    note_completed = True
    note_id = data['note_id']
    note_title = data['note_title']
    user_id = data['user_id']
    user_token = data['user_token']    
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    body = {'completed': "true"}
    print(body)
    resp = requests.patch(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Note successfully Updated" == respJS['message']
    assert note_category == respJS['data']['category']
    assert note_created_at == respJS['data']['created_at']
    assert note_completed == respJS['data']['completed']
    assert note_description == respJS['data']['description']
    assert note_id == respJS['data']['id']
    assert note_title == respJS['data']['title']
    assert user_id == respJS['data']['user_id']
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_status_api_bad_request():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_id = data['note_id']
    user_token = data['user_token']    
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    body = {'completed': "a"}
    print(body)
    resp = requests.patch(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "Note completed status must be boolean" == respJS['message']
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_status_api_unauthorized():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_category = data['note_category']
    note_created_at = data['note_created_at']
    note_description = data['note_description']
    note_completed = True
    note_id = data['note_id']
    note_title = data['note_title']
    user_id = data['user_id']
    user_token = data['user_token']    
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': "@"+user_token}
    body = {'completed': note_completed}
    print(body)
    resp = requests.patch(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message'] 
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_delete_note_api():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_id = data['note_id']
    user_token = data['user_token']
    headers = {'accept': 'application/json', 'x-auth-token': user_token}
    resp = requests.delete(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Note successfully deleted" == respJS['message']
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_delete_note_api_bad_request():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_id = data['note_id']
    user_token = data['user_token']
    headers = {'accept': 'application/json', 'x-auth-token': user_token}
    resp = requests.delete(f"https://practice.expandtesting.com/notes/api/notes/'@'+{note_id}", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "Note ID must be a valid ID" == respJS['message']
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

def test_delete_note_api_unauthorized():
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData)
    login_user_api(randomData)
    create_note_api(randomData)
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    note_id = data['note_id']
    user_token = data['user_token']
    headers = {'accept': 'application/json', 'x-auth-token': '@'+user_token}
    resp = requests.delete(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message']
    delete_user_api(randomData)
    delete_json_file(randomData)
    time.sleep(5)

# def create_user_api(randomData):
#     user_email = Faker().company_email().replace("-", "")
#     user_name = Faker().name()
#     user_password = Faker().password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)
#     body = {'confirmPassword': user_password, 'email': user_email, 'name': user_name, 'password': user_password}
#     headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
#     resp = requests.post("https://practice.expandtesting.com/notes/api/users/register", headers=headers, data=body)
#     respJS = resp.json()
#     assert True == respJS['success']
#     assert 201 == respJS['status']
#     assert "User account created successfully" == respJS['message']
#     assert user_email == respJS['data']['email']
#     assert user_name == respJS['data']['name']
#     user_id = respJS['data']['id']
#     combined_responses = {
#         'user_email': user_email,
#         'user_id': user_id,
#         'user_name': user_name,
#         'user_password': user_password
#     }
#     with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
#         json.dump(combined_responses, json_file, indent=4)

# def login_user_api(randomData):
#     with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
#         data = json.load(json_file)
#     user_email = data['user_email']
#     user_id = data['user_id']    
#     user_password = data['user_password']  
#     user_name = data['user_name']  
#     body = {'email': user_email, 'password': user_password}
#     headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
#     resp = requests.post("https://practice.expandtesting.com/notes/api/users/login", headers=headers, data=body)
#     respJS = resp.json()
#     assert True == respJS['success']
#     assert 200 == respJS['status']
#     assert "Login successful" == respJS['message']
#     assert user_email == respJS['data']['email']
#     assert user_id == respJS['data']['id']
#     assert user_name == respJS['data']['name']
#     user_token = respJS['data']['token']
#     combined_responses = {
#         'user_email': user_email,
#         'user_id': user_id,
#         'user_name': user_name,
#         'user_password': user_password,
#         'user_token': user_token
#     }
#     with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
#         json.dump(combined_responses, json_file, indent=4)
    
# def delete_user_api(randomData):
#     with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
#         data = json.load(json_file)
#     user_token = data['user_token']
#     headers = {'accept': 'application/json', 'x-auth-token': user_token}
#     resp = requests.delete("https://practice.expandtesting.com/notes/api/users/delete-account", headers=headers)
#     respJS = resp.json()
#     assert True == respJS['success']
#     assert 200 == respJS['status']
#     assert "Account successfully deleted" == respJS['message']

# def delete_note_api(randomData):    
#     with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
#         data = json.load(json_file)
#     note_id = data['note_id']
#     user_token = data['user_token']
#     headers = {'accept': 'application/json', 'x-auth-token': user_token}
#     resp = requests.delete(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers)
#     respJS = resp.json()
#     assert True == respJS['success']
#     assert 200 == respJS['status']
#     assert "Note successfully deleted" == respJS['message']

# def create_note_api(randomData):
#     with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
#         data = json.load(json_file)
#     user_id = data['user_id']
#     user_token = data['user_token']
#     note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
#     note_description = Faker().sentence(3)
#     note_title = Faker().sentence(2)
#     body = {'category': note_category, 'description': note_description, 'title': note_title}
#     headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
#     resp = requests.post("https://practice.expandtesting.com/notes/api/notes", headers=headers, data=body)
#     respJS = resp.json()
#     assert True == respJS['success']
#     assert 200 == respJS['status']
#     assert "Note successfully created" == respJS['message']
#     assert note_category == respJS['data']['category']
#     assert note_description == respJS['data']['description']
#     assert note_title == respJS['data']['title']
#     assert user_id == respJS['data']['user_id']
#     note_id = respJS['data']['id']
#     note_created_at = respJS['data']['created_at']
#     note_completed = respJS['data']['completed']
#     note_updated_at = respJS['data']['updated_at']
#     combined_responses = {
#         'note_category': note_category,
#         'note_created_at': note_created_at,
#         'note_completed': note_completed,
#         'note_description': note_description,
#         'note_id': note_id,
#         'note_title': note_title,        
#         'note_updated_at': note_updated_at,
#         'user_id': user_id,
#         'user_token': user_token
#     }
#     with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
#         json.dump(combined_responses, json_file, indent=4)

# def delete_json_file(randomData):
#     os.remove(f"./tests/fixtures/file-{randomData}.json")

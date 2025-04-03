import json
import os
import requests
from faker import Faker





def create_user_api(randomData, setup_database):
    cursor = setup_database.cursor(dictionary=True)
    
    # Seleciona um usuário aleatório do banco de dados
    cursor.execute("SELECT `index`, name, email, password FROM users ORDER BY RAND() LIMIT 1")
    user = cursor.fetchone()

    user_index = user["index"]
    user_name = user["name"]
    user_email = user["email"]
    user_password = user["password"]

    body = {'confirmPassword': user_password, 'email': user_email, 'name': user_name, 'password': user_password}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post("https://practice.expandtesting.com/notes/api/users/register", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)

    assert True == respJS['success']
    assert 201 == respJS['status']
    assert "User account created successfully" == respJS['message']
    assert user_email == respJS['data']['email']
    assert user_name == respJS['data']['name']

    user_id = respJS['data']['id']

    # Atualiza o ID do usuário na mesma linha no banco de dados
    cursor.execute("UPDATE users SET id = %s WHERE `index` = %s", (user_id, user_index))
    setup_database.commit()
    cursor.close()

    # Armazena apenas o índice do usuário escolhido
    user_index_data = {"user_index": user_index}

    with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
        json.dump(user_index_data, json_file, indent=4)

def login_user_api(randomData, setup_database):
   # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, password FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores do banco de dados às variáveis
    user_id = user["id"]
    user_name = user["name"]
    user_email = user["email"]
    user_password = user["password"]

    body = {'email': user_email, 'password': user_password}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post("https://practice.expandtesting.com/notes/api/users/login", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)

    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Login successful" == respJS['message']
    assert user_email == respJS['data']['email']
    assert user_id == respJS['data']['id']
    assert user_name == respJS['data']['name']
    
    # Obtém o token de usuário
    user_token = respJS['data']['token']

    # Atualiza o banco de dados com o token obtido
    cursor.execute("UPDATE users SET token = %s WHERE `index` = %s", (user_token, user_index))
    setup_database.commit()
    cursor.close()

    # Atualiza o objeto com o índice do usuário escolhido
    user_index_data = {"user_index": user_index}

    # Não precisa mais salvar no arquivo JSON, a informação foi atualizada no banco de dados
    # Escreve o índice do usuário no arquivo JSON (se necessário)
    with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
        json.dump(user_index_data, json_file, indent=4)
    
def delete_user_api(randomData, setup_database):
    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar o token do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT token FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui o valor do token à variável user_token
    user_token = user["token"]

    headers = {'accept': 'application/json', 'x-auth-token': user_token}
    resp = requests.delete("https://practice.expandtesting.com/notes/api/users/delete-account", headers=headers)
    respJS = resp.json()
    print(respJS)

    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Account successfully deleted" == respJS['message']

def delete_note_api(randomData):    
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

def create_note_api(randomData):
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
        'note_created_at': note_created_at,
        'note_completed': note_completed,
        'note_description': note_description,
        'note_id': note_id,
        'note_title': note_title,        
        'note_updated_at': note_updated_at,
        'user_id': user_id,
        'user_token': user_token
    }
    with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
        json.dump(combined_responses, json_file, indent=4)

def delete_json_file(randomData):
    os.remove(f"./tests/fixtures/file-{randomData}.json")


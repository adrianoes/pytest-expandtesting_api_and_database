import json
import os
import requests
import mysql.connector
from faker import Faker
import pytest
from mysql.connector import Error

# Configurações do banco de dados
# db_config = {
#     'host': 'localhost',       # Endereço do banco de dados
#     'user': 'root',            # Seu usuário do MySQL
#     'password': '209Scorp!ons',   # Sua senha do MySQL
#     'database': 'users',          #database name
# }

# def connect_to_db():
#     return mysql.connector.connect(**db_config)

# def create_database_and_table():
#     db_connection = connect_to_db()
#     cursor = db_connection.cursor()

#     # Criar banco de dados se não existir
#     cursor.execute("CREATE DATABASE IF NOT EXISTS users;")
#     cursor.execute("USE users;")

#     # Criar tabela se não existir com as colunas conforme solicitado
#     cursor.execute("""
#         CREATE TABLE IF NOT EXISTS users (
#             `index` INT PRIMARY KEY,       -- Agora a coluna chama-se 'index'
#             name VARCHAR(255), 
#             email VARCHAR(255), 
#             password VARCHAR(255), 
#             phone VARCHAR(12), 
#             company VARCHAR(255), 
#             id INT NULL,                  -- Coluna id mantida vazia
#             token VARCHAR(255) NULL       -- Coluna token mantida vazia
#         );
#     """)

#     # # Preencher a tabela com 250 registros vazios (index variando de 1 a 250)
#     # for i in range(1, 251):
#     #     cursor.execute("""
#     #         INSERT INTO users (`index`, name, email, password, phone, company, id, token)
#     #         VALUES (%s, '', '', '', '', '', NULL, NULL);
#     #     """, (i,))
    
#     db_connection.commit()
#     cursor.close()
#     db_connection.close()

# def populate_database_with_random_users():
#     fake = Faker()
#     db_connection = connect_to_db()
#     cursor = db_connection.cursor()

#     for i in range(1, 251):  # 'index' vai de 1 a 250
#         # Gerar dados aleatórios
#         user_name = fake.name()
#         user_email = fake.company_email().replace("-", "")
#         user_password = fake.password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)
#         user_phone = fake.bothify(text='############')
#         user_company = fake.company()

#         # Atualizar a linha na tabela com os dados gerados, usando 'index' como chave primária
#         cursor.execute("""
#             UPDATE users 
#             SET name = %s, email = %s, password = %s, phone = %s, company = %s 
#             WHERE `index` = %s
#         """, (user_name, user_email, user_password, user_phone, user_company, i))

#     db_connection.commit()
#     cursor.close()
#     db_connection.close()

# def get_random_user():
#     db_connection = connect_to_db()
#     cursor = db_connection.cursor()
#     cursor.execute("SELECT * FROM users ORDER BY RAND() LIMIT 1;")
#     user = cursor.fetchone()
#     cursor.close()
#     db_connection.close()
    
#     # Retorna os dados do usuário
#     return {
#         'index': user[0],    # 'index' como identificador
#         'name': user[1],
#         'email': user[2],
#         'password': user[3],
#         'phone': user[4],
#         'company': user[5],
#         'id': user[6],       # A coluna 'id' estará vazia
#         'token': user[7]     # A coluna 'token' estará vazia
#     }

# def check_if_database_exists():
#     db_connection = connect_to_db()
#     cursor = db_connection.cursor()
    
#     cursor.execute("SHOW DATABASES LIKE 'users';")
#     result = cursor.fetchone()
#     if result:
#         print("Database 'users' exists!")
#     else:
#         print("Database 'users' does not exist.")
    
#     cursor.close()
#     db_connection.close()


def create_user_api(randomData):
    user_email = Faker().company_email().replace("-", "")
    user_name = Faker().name()
    user_password = Faker().password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)
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
    combined_responses = {
        'user_email': user_email,
        'user_id': user_id,
        'user_name': user_name,
        'user_password': user_password
    }
    with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
        json.dump(combined_responses, json_file, indent=4)

def login_user_api(randomData):
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_email = data['user_email']
    user_id = data['user_id']    
    user_password = data['user_password']  
    user_name = data['user_name']  
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
    user_token = respJS['data']['token']
    combined_responses = {
        'user_email': user_email,
        'user_id': user_id,
        'user_name': user_name,
        'user_password': user_password,
        'user_token': user_token
    }
    with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
        json.dump(combined_responses, json_file, indent=4)
    
def delete_user_api(randomData):
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_token = data['user_token']
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

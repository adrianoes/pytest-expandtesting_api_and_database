import os
import mysql.connector
import pytest
from faker import Faker
from dotenv import load_dotenv
import time
import json
import requests
from .support_api import create_user_api, delete_json_file, delete_user_api, login_user_api

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'users'),
}

# Inicializa o Faker
fake = Faker()

@pytest.fixture(scope="session")
def connection():
    """Cria uma conexão com o MySQL"""
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        yield conn
    finally:
        if conn.is_connected():
            conn.close()

@pytest.fixture(scope="session")
def create_database(connection):
    """Cria o banco de dados se ele não existir"""
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
    cursor.close()

@pytest.fixture(scope="session")
def setup_database(connection, create_database):
    """Conecta no banco de dados criado"""
    conn = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )
    yield conn
    if conn.is_connected():
        conn.close()

@pytest.fixture(scope="session")
def create_table(setup_database):
    """Cria a tabela de usuários"""
    cursor = setup_database.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            `index` INT AUTO_INCREMENT PRIMARY KEY,
            id VARCHAR(255) NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            company VARCHAR(255) NOT NULL,
            phone VARCHAR(255) NOT NULL,
            token VARCHAR(255) NULL
        )
    """)
    cursor.close()

@pytest.fixture(scope="session")
def insert_users(setup_database, create_table):
    """Insere 250 usuários na tabela"""
    cursor = setup_database.cursor()
    
    for _ in range(250):
        name = fake.name()
        email = fake.lexify(text='??').lower() + fake.company_email().replace("-", "")
        password = fake.password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)
        company = fake.company()[:24]
        phone = fake.bothify(text='############')
        token = None  # Deixando o token em branco (NULL)

        # Inserção no banco de dados (não inserindo `id` ou `token`, que serão NULL)
        cursor.execute("""
            INSERT INTO users (name, email, password, company, phone)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, password, company, phone))
    
    setup_database.commit()  # Confirma a inserção
    cursor.close()

@pytest.fixture(scope="session", autouse=True)
def teardown_database(setup_database):
    """Exclui o banco de dados após todos os testes serem executados"""
    yield  # Executa os testes antes de remover o banco
    
    cursor = setup_database.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {db_config['database']}")
    setup_database.commit()
    cursor.close()
    setup_database.close()
    print("\n🔥 Banco de dados excluído após os testes!")

def test_create_user_api(setup_database, create_table, insert_users):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
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

    user_id = respJS['data']['id']

    # Atualiza o ID do usuário na mesma linha no banco de dados
    cursor.execute("UPDATE users SET id = %s WHERE `index` = %s", (user_id, user_index))
    setup_database.commit()

    cursor.execute("SELECT id FROM users WHERE `index` = %s", (user_index,))
    db_user = cursor.fetchone()
    cursor.close()

    assert True == respJS['success']
    assert 201 == respJS['status']
    assert "User account created successfully" == respJS['message']
    assert user_email == respJS['data']['email']
    assert user_name == respJS['data']['name']
    assert db_user['id'] == user_id #database validation

    # Armazena apenas o índice do usuário escolhido
    user_index_data = {"user_index": user_index}

    with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
        json.dump(user_index_data, json_file, indent=4)

    login_user_api(randomData,  setup_database)
    delete_user_api(randomData,  setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_create_user_api_bad_request(setup_database):
    cursor = setup_database.cursor(dictionary=True)
    # Seleciona um usuário aleatório do banco de dados
    cursor.execute("SELECT `index`, name, email, password FROM users ORDER BY RAND() LIMIT 1")
    user = cursor.fetchone()
    user_name = user["name"]
    user_email = user["email"]
    user_password = user["password"]
    body = {'confirmPassword': user_password, 'email': '@'+user_email, 'name': user_name, 'password': user_password}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post("https://practice.expandtesting.com/notes/api/users/register", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "A valid email address is required" == respJS['message']
    time.sleep(5)

def test_login_user_api(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)

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

    # Obtém o token de usuário
    user_token = respJS['data']['token']

    # Atualiza o banco de dados com o token obtido
    cursor.execute("UPDATE users SET token = %s WHERE `index` = %s", (user_token, user_index))
    setup_database.commit()

    # Consulta o token no banco para validação
    cursor.execute("SELECT token FROM users WHERE `index` = %s", (user_index,))
    db_user = cursor.fetchone()
    cursor.close()

    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Login successful" == respJS['message']
    assert user_email == respJS['data']['email']
    assert user_id == respJS['data']['id']
    assert user_name == respJS['data']['name']
    assert db_user['token'] == user_token  # database validation

    # Atualiza o objeto com o índice do usuário escolhido
    user_index_data = {"user_index": user_index}

    # Não precisa mais salvar no arquivo JSON, a informação foi atualizada no banco de dados
    # Escreve o índice do usuário no arquivo JSON (se necessário)
    with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
        json.dump(user_index_data, json_file, indent=4)

    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_login_user_api_bad_request(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, password FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores do banco de dados às variáveis
    user_email = user["email"]
    user_password = user["password"]
    body = {'email': '@'+user_email, 'password': user_password}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post("https://practice.expandtesting.com/notes/api/users/login", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "A valid email address is required" == respJS['message']
    login_user_api(randomData, setup_database)
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_login_user_api_unauthorized(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT id, name, email, password FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores do banco de dados às variáveis
    user_email = user["email"]
    user_password = user["password"]
    body = {'email': user_email, 'password': '@'+user_password}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
    resp = requests.post("https://practice.expandtesting.com/notes/api/users/login", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Incorrect email address or password" == respJS['message']
    login_user_api(randomData, setup_database)
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_get_user_api(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)

    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT name, email, id, token FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    user_name = user["name"]
    user_email = user["email"]
    user_id = user["id"]
    user_token = user["token"]

    headers = {'accept': 'application/json', 'x-auth-token': user_token}
    resp = requests.get("https://practice.expandtesting.com/notes/api/users/profile", headers=headers)
    respJS = resp.json()
    print(respJS)

    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Profile successful" == respJS['message']
    assert user_email == respJS['data']['email']
    assert user_id == respJS['data']['id']
    assert user_name == respJS['data']['name']

    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_get_user_api_unauthorized(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)
    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT name, email, id, token FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    user_token = user["token"]
    headers = {'accept': 'application/json', 'x-auth-token': "@"+user_token}
    resp = requests.get("https://practice.expandtesting.com/notes/api/users/profile", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message']
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_user_api(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)

    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT name, email, id, phone, company, token FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    user_name = user["name"]
    user_email = user["email"]
    user_id = user["id"]
    user_phone = user["phone"]
    user_company = user["company"]
    user_token = user["token"]

    # Atualiza alguns dados do usuário para enviar na requisição
    new_user_name = Faker().name()
    new_user_phone = Faker().bothify(text='############')
    new_user_company = Faker().company()
    body = {'company': new_user_company, 'phone': new_user_phone, 'name': new_user_name}
    print(body)

    # Cabeçalhos da requisição
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}

    # Realiza a requisição para atualizar o perfil
    resp = requests.patch("https://practice.expandtesting.com/notes/api/users/profile", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)

    # Grava os dados atualizados no banco
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("""
        UPDATE users
        SET name = %s, phone = %s, company = %s
        WHERE `index` = %s
    """, (new_user_name, new_user_phone, new_user_company, user_index))
    setup_database.commit()

    # Consulta os dados para validação
    cursor.execute("SELECT name, phone, company FROM users WHERE `index` = %s", (user_index,))
    db_user = cursor.fetchone()
    cursor.close()

    # Validações das respostas da API
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Profile updated successful" == respJS['message']
    assert new_user_company == respJS['data']['company']
    assert user_email == respJS['data']['email']
    assert user_id == respJS['data']['id']
    assert new_user_name == respJS['data']['name']
    assert new_user_phone == respJS['data']['phone']

    # Validações com os dados do banco
    assert db_user['name'] == new_user_name  # database validation
    assert db_user['phone'] == new_user_phone  # database validation
    assert db_user['company'] == new_user_company  # database validation

    # Deleta o usuário e o arquivo JSON após o teste
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_user_api_bad_request(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)
    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT name, email, id, phone, company, token FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    user_name = user["name"]
    user_email = user["email"]
    user_id = user["id"]
    user_phone = user["phone"]
    user_company = user["company"]
    user_token = user["token"]

    # Atualiza alguns dados do usuário para enviar na requisição
    new_user_name = 'a'
    new_user_phone = Faker().bothify(text='############')
    new_user_company = Faker().company()
    body = {'company': new_user_company, 'phone': new_user_phone, 'name': new_user_name}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    resp = requests.patch("https://practice.expandtesting.com/notes/api/users/profile", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "User name must be between 4 and 30 characters" == respJS['message']
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_user_api_unauthorized(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)

    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT name, email, id, phone, company, token FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    user_name = user["name"]
    user_email = user["email"]
    user_id = user["id"]
    user_phone = user["phone"]
    user_company = user["company"]
    user_token = user["token"]

    # Atualiza alguns dados do usuário para enviar na requisição
    new_user_name = Faker().name()
    new_user_phone = Faker().bothify(text='############')
    new_user_company = Faker().company()
    body = {'company': new_user_company, 'phone': new_user_phone, 'name': new_user_name}
    print(body)

    # Cabeçalhos da requisição, simulando um erro de autorização ao alterar o token
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': '@' + user_token}

    # Realiza a requisição para atualizar o perfil
    resp = requests.patch("https://practice.expandtesting.com/notes/api/users/profile", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)

    # Validações para a resposta da API de erro de autorização
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message']

    # Deleta o usuário e o arquivo JSON após o teste
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_user_password_api(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)

    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT name, email, id, password, token FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    user_password = user["password"]
    user_id = user["id"]
    user_token = user["token"]
    
    # Gerar uma nova senha
    user_new_password = Faker().password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)

    body = {'currentPassword': user_password, 'newPassword': user_new_password}
    print(body)

    # Realiza a requisição para atualizar a senha
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    resp = requests.post("https://practice.expandtesting.com/notes/api/users/change-password", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)

    # Atualiza a nova senha no banco
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("UPDATE users SET password = %s WHERE `index` = %s", (user_new_password, user_index))
    setup_database.commit()

    # Consulta a senha atualizada para validar
    cursor.execute("SELECT password FROM users WHERE `index` = %s", (user_index,))
    db_user = cursor.fetchone()
    cursor.close()

    # Validações para a resposta da API de sucesso
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "The password was successfully updated" == respJS['message']
    assert db_user['password'] == user_new_password  # database validation

    # Deleta o usuário e o arquivo JSON após o teste
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_user_password_api_bad_request(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)

    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT name, email, id, password, token FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    user_password = user["password"]
    user_token = user["token"]
    
    # Corpo da requisição com senha inválida
    body = {'currentPassword': user_password, 'newPassword': "123"}
    print(body)

    # Realiza a requisição para tentar atualizar a senha com senha inválida
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    resp = requests.post("https://practice.expandtesting.com/notes/api/users/change-password", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)

    # Validações para a resposta da API de erro de requisição ruim (400)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "New password must be between 6 and 30 characters" == respJS['message']

    # Deleta o usuário e o arquivo JSON após o teste
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_user_password_api_unauthorized(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)

    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database.cursor(dictionary=True)
    cursor.execute("SELECT name, email, id, password, token FROM users WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    user_password = user["password"]
    user_token = user["token"]
    
    # Gerar uma nova senha
    user_new_password = Faker().password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)

    body = {'currentPassword': user_password, 'newPassword': user_new_password}
    print(body)

    # Simula um erro de autorização com um token inválido
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': "@" + user_token}
    resp = requests.post("https://practice.expandtesting.com/notes/api/users/change-password", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)

    # Validações para a resposta da API de erro de autorização
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message']

    # Deleta o usuário e o arquivo JSON após o teste
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_logout_user_api(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)
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
    resp = requests.delete("https://practice.expandtesting.com/notes/api/users/logout", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "User has been successfully logged out" == respJS['message']
    login_user_api(randomData, setup_database)
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_logout_user_api_unauthorized(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)
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
    headers = {'accept': 'application/json', 'x-auth-token': '@'+user_token}
    resp = requests.delete("https://practice.expandtesting.com/notes/api/users/logout", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message']
    delete_user_api(randomData, setup_database)
    delete_json_file(randomData)
    time.sleep(5)

def test_delete_user_api(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)

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

    delete_json_file(randomData)
    time.sleep(5)

def test_delete_user_api_unauthorized(setup_database):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user_api(randomData, setup_database)
    login_user_api(randomData, setup_database)
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
    headers = {'accept': 'application/json', 'x-auth-token': '@'+user_token}
    resp = requests.delete("https://practice.expandtesting.com/notes/api/users/delete-account", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message']

    delete_user_api(randomData, setup_database)

    delete_json_file(randomData)
    time.sleep(5)



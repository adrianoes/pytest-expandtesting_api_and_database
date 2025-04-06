import os
import mysql.connector
import pytest
from faker import Faker
from dotenv import load_dotenv
import time
import json
import requests
from .support_api import create_note_api, create_user4Notes_api, delete_json_file, delete_note_api, delete_user4Notes_api, login_user4Notes_api

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

db_config4Notes = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME_N', 'notes'),
}

# Inicializa o Faker
fake = Faker()

@pytest.fixture(scope="session")
def connection4Notes():
    """Cria uma conexão com o MySQL"""
    try:
        conn = mysql.connector.connect(
            host=db_config4Notes['host'],
            user=db_config4Notes['user'],
            password=db_config4Notes['password']
        )
        yield conn
    finally:
        if conn.is_connected():
            conn.close()

@pytest.fixture(scope="session")
def create_database4Notes(connection4Notes):
    """Cria o banco de dados se ele não existir"""
    cursor = connection4Notes.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config4Notes['database']}")
    cursor.close()

@pytest.fixture(scope="session")
def setup_database4Notes(connection4Notes, create_database4Notes):
    """Conecta no banco de dados criado"""
    conn = mysql.connector.connect(
        host=db_config4Notes['host'],
        user=db_config4Notes['user'],
        password=db_config4Notes['password'],
        database=db_config4Notes['database']
    )
    yield conn
    if conn.is_connected():
        conn.close()

@pytest.fixture(scope="session")
def create_table4Notes(setup_database4Notes):
    """Cria a tabela de notas e usuários"""
    cursor = setup_database4Notes.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            `index` INT AUTO_INCREMENT PRIMARY KEY,
            id VARCHAR(255) NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            company VARCHAR(255) NOT NULL,
            phone VARCHAR(255) NOT NULL,
            token VARCHAR(255) NULL,
            noteId VARCHAR(255) NULL,
            noteTitle VARCHAR(255) NOT NULL,
            noteDescription VARCHAR(255) NOT NULL,
            noteCompleted VARCHAR(255) NULL,
            noteCreatedAt VARCHAR(255) NULL,
            noteUpdatedAt VARCHAR(255) NULL,
            noteCategory VARCHAR(255) NOT NULL
        )
    """)
    cursor.close()

@pytest.fixture(scope="session")
def insert_users4Notes(setup_database4Notes, create_table4Notes):
    """Insere 250 notas na tabela"""
    cursor = setup_database4Notes.cursor()
    
    for _ in range(250):
        name = fake.name()
        email = fake.lexify(text='??').lower() + fake.company_email().replace("-", "")
        password = fake.password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)
        company = fake.company()[:24]
        phone = fake.bothify(text='############')
        token = None  # Inicialmente vazio
        noteTitle = fake.sentence(4)
        noteDescription = fake.sentence(5)
        noteCategory = fake.random_element(elements=('Home', 'Personal', 'Work'))

        cursor.execute("""
            INSERT INTO notes (name, email, password, company, phone, noteTitle, noteDescription, noteCategory)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, email, password, company, phone, noteTitle, noteDescription, noteCategory))
    
    setup_database4Notes.commit()
    cursor.close()

@pytest.fixture(scope="session", autouse=True)
def teardown_database4Notes(setup_database4Notes):
    """Exclui o banco de dados após todos os testes serem executados"""
    yield  # Executa os testes antes de remover o banco
    
    cursor = setup_database4Notes.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {db_config4Notes['database']}")
    setup_database4Notes.commit()
    cursor.close()
    setup_database4Notes.close()
    print("\n🔥 Banco de dados excluído após os testes!")

def test_create_note_api(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário e da nota pelo index
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT id, token, noteTitle, noteDescription, noteCategory FROM notes WHERE `index` = %s", (user_index,))
    user_note = cursor.fetchone()

    # Atribui os valores do banco de dados às variáveis
    user_id = user_note["id"]
    user_token = user_note["token"]
    note_title = user_note["noteTitle"]
    note_description = user_note["noteDescription"]
    note_category = user_note["noteCategory"]

    body = {'category': note_category, 'description': note_description, 'title': note_title}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    resp = requests.post("https://practice.expandtesting.com/notes/api/notes", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)

    note_id = respJS['data']['id']
    note_created_at = respJS['data']['created_at']
    note_completed = respJS['data']['completed']
    note_updated_at = respJS['data']['updated_at']

    # Assertions de validação no banco de dados e API
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Note successfully created" == respJS['message']
    assert note_category == respJS['data']['category']
    assert note_description == respJS['data']['description']
    assert note_title == respJS['data']['title']
    assert user_id == respJS['data']['user_id']

    # Atualiza os dados da nota na linha do usuário correspondente ao user_index
    cursor = setup_database4Notes.cursor()
    cursor.execute("""
        UPDATE notes 
        SET noteId = %s, noteCompleted = %s, 
            noteCreatedAt = %s, noteUpdatedAt = %s
        WHERE `index` = %s
    """, (note_id, note_completed, note_created_at, note_updated_at, user_index))
    setup_database4Notes.commit()

    # Consulta novamente para validar os dados salvos
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteId, noteCompleted, noteCreatedAt, noteUpdatedAt FROM notes WHERE `index` = %s", (user_index,))
    db_note = cursor.fetchone()
    cursor.close()

    # Assertions com os dados do banco de dados
    assert db_note['noteId'] == note_id
    assert bool(int(db_note['noteCompleted'])) == note_completed
    assert db_note['noteCreatedAt'] == note_created_at
    assert db_note['noteUpdatedAt'] == note_updated_at

    # Armazena apenas o índice do usuário escolhido no arquivo JSON
    user_index_data = {"user_index": user_index}
    
    with open(f"./tests/fixtures/file-{randomData}.json", 'w') as json_file:
        json.dump(user_index_data, json_file, indent=4)

    # This functions is here only for practice purpose since we already have delete_user_api to delete the user right away.
    delete_note_api(randomData, setup_database4Notes)
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_create_note_api_bad_request(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário e da nota pelo index
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT id, token, noteTitle, noteDescription, noteCategory FROM notes WHERE `index` = %s", (user_index,))
    user_note = cursor.fetchone()

    # Atribui os valores do banco de dados às variáveis
    user_id = user_note["id"]
    user_token = user_note["token"]
    note_title = user_note["noteTitle"]
    note_description = user_note["noteDescription"]
    note_category = user_note["noteCategory"]
    body = {'category': 'a', 'description': note_description, 'title': note_title}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    resp = requests.post("https://practice.expandtesting.com/notes/api/notes", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "Category must be one of the categories: Home, Work, Personal" == respJS['message']
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_create_note_api_unauthorized(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário e da nota pelo index
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT id, token, noteTitle, noteDescription, noteCategory FROM notes WHERE `index` = %s", (user_index,))
    user_note = cursor.fetchone()

    # Atribui os valores do banco de dados às variáveis
    user_id = user_note["id"]
    user_token = user_note["token"]
    note_title = user_note["noteTitle"]
    note_description = user_note["noteDescription"]
    note_category = user_note["noteCategory"]
    body = {'category': note_category, 'description': note_description, 'title': note_title}
    print(body)
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': '@'+user_token}
    resp = requests.post("https://practice.expandtesting.com/notes/api/notes", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message']
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_get_notes_api(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT id, token FROM notes WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    user_id = user["id"]
    user_token = user["token"]
    note_category_array = [Faker().random_element(elements=('Home', 'Personal', 'Work')), 'Home', 'Personal', 'Work']
    note_created_at_array = ["a", "b", "c", "d"]
    note_completed_array = [False, False, False, True]
    note_id_array = ["a", "b", "c", "d"]
    note_updated_at_array = ["a", "b", "c", "d"]
    note_description_array = [Faker().sentence(5), Faker().sentence(5), Faker().sentence(5), Faker().sentence(5)]
    note_title_array = [Faker().sentence(4), Faker().sentence(4), Faker().sentence(4), Faker().sentence(4)]
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

    # Insere as outras 3 notas no banco como novas linhas com os mesmos dados de usuário
    cursor = setup_database4Notes.cursor(dictionary=True)

    # Primeiro, pega todos os dados do usuário original (linha base)
    cursor.execute("SELECT * FROM notes WHERE `index` = %s", (user_index,))
    user_row = cursor.fetchone()

    # Atualiza a linha original com os dados da primeira nota
    update_query = """
        UPDATE notes SET
            noteId = %s,
            noteTitle = %s,
            noteDescription = %s,
            noteCompleted = %s,
            noteCreatedAt = %s,
            noteUpdatedAt = %s,
            noteCategory = %s
        WHERE `index` = %s
    """
    cursor.execute(update_query, (
        note_id_array[0],
        note_title_array[0],
        note_description_array[0],
        str(note_completed_array[0]),
        note_created_at_array[0],
        note_updated_at_array[0],
        note_category_array[0],
        user_index
    ))

    # Move os usuários que vêm depois para frente (incrementa os índices)
    cursor.execute("UPDATE notes SET `index` = `index` + 3 WHERE `index` > %s ORDER BY `index` DESC", (user_index,))

    # Insere as outras 3 notas como novas linhas (copiando os dados de usuário)
    insert_query = """
        INSERT INTO notes (
            `index`, id, name, email, password, company, phone, token,
            noteId, noteTitle, noteDescription, noteCompleted,
            noteCreatedAt, noteUpdatedAt, noteCategory
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for i in range(1, 4):  # notas 1, 2 e 3 (as outras 3 além da original)
        new_index = user_index + i        
 
        new_email = str(i) + "same@as.above.com"  # Para as outras linhas, o email fica vazio (NULL)
        print(new_email)
        cursor.execute(insert_query, (
            new_index,
            user_row['id'],
            user_row['name'],
            new_email,  # email será preenchido apenas para a primeira linha
            user_row['password'],
            user_row['company'],
            user_row['phone'],
            user_row['token'],
            note_id_array[i],
            note_title_array[i],
            note_description_array[i],
            str(note_completed_array[i]),
            note_created_at_array[i],
            note_updated_at_array[i],
            note_category_array[i]
        ))

    setup_database4Notes.commit()
    # cursor.close()

        # Faz assert de cada uma das 4 notas: API vs banco de dados
    for i in range(4):
        note_id = note_id_array[i]

        # Consulta no banco os dados da nota pelo noteId
        cursor.execute("""
            SELECT 
                noteId, 
                noteTitle, 
                noteDescription, 
                noteCompleted, 
                noteCreatedAt, 
                noteUpdatedAt, 
                noteCategory 
            FROM notes 
            WHERE noteId = %s
        """, (note_id,))
        db_note = cursor.fetchone()

        assert db_note is not None, f"Nota com ID {note_id} não encontrada no banco"

        # Comparações (convertendo se necessário)
        assert db_note['noteId'] == note_id
        assert db_note['noteTitle'] == note_title_array[i]
        assert db_note['noteDescription'] == note_description_array[i]
        assert db_note['noteCompleted'] in [str(note_completed_array[i]), note_completed_array[i], "1" if note_completed_array[i] else "0", None]  # dependendo como armazena
        assert db_note['noteCreatedAt'] == note_created_at_array[i]
        assert db_note['noteUpdatedAt'] == note_updated_at_array[i]
        assert db_note['noteCategory'] == note_category_array[i]

    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_get_notes_api_unauthorized(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    # Abre o arquivo para obter o index do usuário escolhido aleatoriamente
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)
    user_index = data['user_index']

    # Conecta ao banco de dados para buscar os dados do usuário pelo index
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT id, token FROM notes WHERE `index` = %s", (user_index,))
    user = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    user_id = user["id"]
    user_token = user["token"]
    note_category_array = [Faker().random_element(elements=('Home', 'Personal', 'Work')), 'Home', 'Personal', 'Work']
    note_created_at_array = ["a", "b", "c", "d"]
    note_completed_array = [False, False, False, True]
    note_id_array = ["a", "b", "c", "d"]
    note_updated_at_array = ["a", "b", "c", "d"]
    note_description_array = [Faker().sentence(5), Faker().sentence(5), Faker().sentence(5), Faker().sentence(5)]
    note_title_array = [Faker().sentence(4), Faker().sentence(4), Faker().sentence(4), Faker().sentence(4)]
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
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_get_note_api(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteCategory, noteCreatedAt, noteCompleted, noteDescription, noteId, noteTitle, noteUpdatedAt, id, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    note_category = note_row['noteCategory']
    note_created_at = note_row['noteCreatedAt']
    note_completed = bool(int(note_row['noteCompleted']))  # Converte '0' ou '1' para False ou True
    note_description = note_row['noteDescription']
    note_id = note_row['noteId']
    note_title = note_row['noteTitle']
    note_updated_at = note_row['noteUpdatedAt']
    user_id = note_row['id']
    user_token = note_row['token']

    cursor.close()

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

    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_get_note_api_unauthorized(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteCategory, noteCreatedAt, noteCompleted, noteDescription, noteId, noteTitle, noteUpdatedAt, id, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    note_category = note_row['noteCategory']
    note_created_at = note_row['noteCreatedAt']
    note_completed = note_row['noteCompleted']
    note_description = note_row['noteDescription']
    note_id = note_row['noteId']
    note_title = note_row['noteTitle']
    note_updated_at = note_row['noteUpdatedAt']
    user_id = note_row['id']
    user_token = note_row['token']

    cursor.close()

    headers = {'accept': 'application/json', 'x-auth-token': '@'+user_token}
    resp = requests.get(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message'] 
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_api(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteCategory, noteCreatedAt, noteCompleted, noteDescription, noteId, noteTitle, id, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    note_created_at = note_row['noteCreatedAt']
    note_completed = True  # Aqui, conforme a lógica do teste, sempre será True
    note_id = note_row['noteId']
    user_id = note_row['id']
    user_token = note_row['token']
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_description = Faker().sentence(5) 
    note_title = Faker().sentence(4) 

    cursor.close()

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

    note_updated_at = respJS['data']['updated_at']

    # Atualiza os dados da nota na linha do usuário correspondente ao user_index no banco
    cursor = setup_database4Notes.cursor()
    cursor.execute("""
        UPDATE notes 
        SET noteCategory = %s, noteDescription = %s, noteTitle = %s, 
            noteCompleted = %s, noteUpdatedAt = %s
        WHERE `index` = %s
    """, (note_category, note_description, note_title, note_completed, note_updated_at, user_index))
    setup_database4Notes.commit()
    cursor.close()

    # Consulta os dados atualizados do banco para validação (somente os campos desejados)
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("""
        SELECT noteCategory, noteDescription, noteTitle, noteCompleted, noteUpdatedAt
        FROM notes 
        WHERE noteId = %s
    """, (note_id,))
    db_note = cursor.fetchone()
    cursor.close()

    # Assertions comparando os valores da resposta da API com os valores persistidos no banco
    assert db_note['noteCategory'] == respJS['data']['category']
    assert db_note['noteDescription'] == respJS['data']['description']
    assert db_note['noteTitle'] == respJS['data']['title']
    assert bool(int(db_note['noteCompleted'])) == respJS['data']['completed']
    assert db_note['noteUpdatedAt'] == respJS['data']['updated_at']

    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_api_bad_request(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteCategory, noteCreatedAt, noteCompleted, noteDescription, noteId, noteTitle, id, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    note_created_at = note_row['noteCreatedAt']
    note_completed = True  # Aqui, conforme a lógica do teste, sempre será True
    note_id = note_row['noteId']
    user_id = note_row['id']
    user_token = note_row['token']
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_description = Faker().sentence(5) 
    note_title = Faker().sentence(4) 

    cursor.close()

    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    body = {'category': 'a', 'completed': "true", 'description': note_description, 'title': note_title}
    print(body)
    resp = requests.put(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "Category must be one of the categories: Home, Work, Personal" == respJS['message']
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_api_unauthorized(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteCategory, noteCreatedAt, noteCompleted, noteDescription, noteId, noteTitle, id, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    note_created_at = note_row['noteCreatedAt']
    note_completed = True  # Aqui, conforme a lógica do teste, sempre será True
    note_id = note_row['noteId']
    user_id = note_row['id']
    user_token = note_row['token']
    note_category = Faker().random_element(elements=('Home', 'Personal', 'Work'))
    note_description = Faker().sentence(5) 
    note_title = Faker().sentence(4) 

    cursor.close()
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': "@"+user_token}
    body = {'category': note_category, 'completed': "true", 'description': note_description, 'title': note_title}
    print(body)
    resp = requests.put(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message'] 
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_status_api(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteCategory, noteCreatedAt, noteCompleted, noteDescription, noteId, noteTitle, id, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    note_created_at = note_row['noteCreatedAt']
    note_completed = True  # Aqui, conforme a lógica do teste, sempre será True
    note_id = note_row['noteId']
    user_id = note_row['id']
    user_token = note_row['token']
    note_category = note_row['noteCategory'] 
    note_description = note_row['noteDescription']
    note_title = note_row['noteTitle']
    cursor.close()

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

    # Atualiza o status "completed" da nota no banco de dados (caso não seja automaticamente persistido)
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("UPDATE notes SET noteCompleted = %s WHERE noteId = %s", (respJS['data']['completed'], note_id))
    setup_database4Notes.commit()
    
    # Consulta o banco para validar o status atualizado
    cursor.execute("SELECT noteCompleted FROM notes WHERE noteId = %s", (note_id,))
    db_note = cursor.fetchone()
    cursor.close()

    # Assertion para validar que o campo 'noteCompleted' no banco corresponde ao valor retornado pela API
    assert bool(int(db_note['noteCompleted'])) == respJS['data']['completed']

    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_status_api_bad_request(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteCategory, noteCreatedAt, noteCompleted, noteDescription, noteId, noteTitle, id, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    note_created_at = note_row['noteCreatedAt']
    note_completed = True  # Aqui, conforme a lógica do teste, sempre será True
    note_id = note_row['noteId']
    user_id = note_row['id']
    user_token = note_row['token']
    note_category = note_row['noteCategory'] 
    note_description = note_row['noteDescription']
    note_title = note_row['noteTitle']

    cursor.close()   
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': user_token}
    body = {'completed': "a"}
    print(body)
    resp = requests.patch(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "Note completed status must be boolean" == respJS['message']
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_update_note_status_api_unauthorized(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteCategory, noteCreatedAt, noteCompleted, noteDescription, noteId, noteTitle, id, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    # Atribui os valores das colunas do banco às variáveis
    note_created_at = note_row['noteCreatedAt']
    note_completed = True  # Aqui, conforme a lógica do teste, sempre será True
    note_id = note_row['noteId']
    user_id = note_row['id']
    user_token = note_row['token']
    note_category = note_row['noteCategory'] 
    note_description = note_row['noteDescription']
    note_title = note_row['noteTitle']

    cursor.close()     
    headers = {'accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded', 'x-auth-token': "@"+user_token}
    body = {'completed': note_completed}
    print(body)
    resp = requests.patch(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers, data=body)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message'] 
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_delete_note_api(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteId, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    user_token = note_row['token']  
    note_id = note_row['noteId']

    headers = {'accept': 'application/json', 'x-auth-token': user_token}
    resp = requests.delete(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert True == respJS['success']
    assert 200 == respJS['status']
    assert "Note successfully deleted" == respJS['message']
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_delete_note_api_bad_request(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteId, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    user_token = note_row['token']  
    note_id = note_row['noteId']
    headers = {'accept': 'application/json', 'x-auth-token': user_token}
    resp = requests.delete(f"https://practice.expandtesting.com/notes/api/notes/'@'+{note_id}", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 400 == respJS['status']
    assert "Note ID must be a valid ID" == respJS['message']
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

def test_delete_note_api_unauthorized(setup_database4Notes, create_table4Notes, insert_users4Notes):
    randomData = Faker().hexify(text='^^^^^^^^^^^^')
    create_user4Notes_api(randomData, setup_database4Notes)
    login_user4Notes_api(randomData, setup_database4Notes)
    create_note_api(randomData, setup_database4Notes)
    # Lê o arquivo JSON para obter o índice aleatório
    with open(f"./tests/fixtures/file-{randomData}.json", 'r') as json_file:
        data = json.load(json_file)

    # Pega o índice do arquivo JSON
    user_index = data['user_index']

    # Conecta ao banco de dados e pega os dados da linha correspondente ao índice
    cursor = setup_database4Notes.cursor(dictionary=True)
    cursor.execute("SELECT noteId, token FROM notes WHERE `index` = %s", (user_index,))
    note_row = cursor.fetchone()

    user_token = note_row['token']  
    note_id = note_row['noteId']
    headers = {'accept': 'application/json', 'x-auth-token': '@'+user_token}
    resp = requests.delete(f"https://practice.expandtesting.com/notes/api/notes/{note_id}", headers=headers)
    respJS = resp.json()
    print(respJS)
    assert False == respJS['success']
    assert 401 == respJS['status']
    assert "Access token is not valid or has expired, you will need to login" == respJS['message']
    delete_user4Notes_api(randomData, setup_database4Notes)
    delete_json_file(randomData)
    time.sleep(5)

import os
import mysql.connector
import pytest
from faker import Faker
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Agora, as variáveis de ambiente serão carregadas automaticamente
db_config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'users'),
}

# Inicializa o Faker
fake = Faker()

@pytest.fixture(scope="module")
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

@pytest.fixture(scope="module")
def create_database(connection):
    """Cria o banco de dados se ele não existir"""
    cursor = connection.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_config['database']}")
    cursor.close()

@pytest.fixture(scope="module")
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

@pytest.fixture(scope="module")
def create_table(setup_database):
    """Cria a tabela de usuários"""
    cursor = setup_database.cursor()
    
    # Corrigido para remover o comentário que causava erro de sintaxe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            `index` INT AUTO_INCREMENT PRIMARY KEY,
            id INT NULL,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            company VARCHAR(255) NOT NULL,
            phone VARCHAR(255) NOT NULL,
            token VARCHAR(255) NULL
        )
    """)
    cursor.close()

@pytest.fixture(scope="module")
def insert_users(setup_database, create_table):
    """Insere 250 usuários na tabela"""
    cursor = setup_database.cursor()
    
    for _ in range(250):
        name = fake.name()
        email = fake.company_email().replace("-", "")
        password = fake.password(length=12, special_chars=False, digits=True, upper_case=True, lower_case=True)
        company = fake.company()
        phone = fake.bothify(text='############')
        token = None  # Deixando o token em branco (NULL)

        # Inserção no banco de dados (não inserindo `id` ou `token`, que serão NULL)
        cursor.execute("""
            INSERT INTO users (name, email, password, company, phone)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, password, company, phone))
    
    setup_database.commit()  # Confirma a inserção
    cursor.close()

def test_create_database(setup_database, insert_users):
    """Valida se o banco de dados foi criado com sucesso"""
    cursor = setup_database.cursor()
    cursor.execute("SHOW DATABASES LIKE %s", (db_config['database'],))
    result = cursor.fetchone()
    cursor.close()
    
    assert result is not None, f"Banco de dados {db_config['database']} não encontrado!"

def test_user_insertion(setup_database, insert_users):
    """Valida se os usuários foram inseridos corretamente"""
    cursor = setup_database.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    result = cursor.fetchone()
    cursor.close()
    
    assert result[0] == 250, f"Esperado 250 usuários, mas encontrou {result[0]}!"

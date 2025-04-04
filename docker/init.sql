CREATE DATABASE IF NOT EXISTS users;
CREATE DATABASE IF NOT EXISTS notes;

GRANT ALL PRIVILEGES ON users.* TO 'test_user'@'%';
GRANT ALL PRIVILEGES ON notes.* TO 'test_user'@'%';
GRANT CREATE ON *.* TO 'test_user'@'%';  -- Permissão para criar bancos de dados

FLUSH PRIVILEGES;

from cryptography.fernet import Fernet

# Генерация ключа
key = Fernet.generate_key()
print(key.decode())  # Вывод ключа для использования в .env файле
from docpub.settings import CONVERT


def decryption(password_encrypted):
    password_encoded = password_encrypted.encode()
    password_decrypted = CONVERT.decrypt(password_encoded)
    password = password_decrypted.decode()
    return password
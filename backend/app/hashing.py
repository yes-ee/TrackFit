# app/hashing.py

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Hasher:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        print(f"--- Verifying password of length: {len(plain_password)} ---")
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        print(f"--- Hashing password of length: {len(password)} ---")
        print(f"--- Password value (first 10 chars): '{password[:10]}' ---")
        return pwd_context.hash(password)
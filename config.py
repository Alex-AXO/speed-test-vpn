import os
from dotenv import load_dotenv

load_dotenv()


API_TOKEN = os.getenv('API_TOKEN')

ADMIN1 = int(os.getenv('ADMIN1'))
ADMINS = ADMIN1,

FILE = 'test10.zip'     # test10.zip | test100.zip | test500.zip

PORT = 2023

DB_PATH = "speedtest.db"  # Путь к базе данных

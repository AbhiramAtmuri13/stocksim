import os
from dotenv import load_dotenv
load_dotenv()

print("USER:", os.getenv("DB_USER"))
print("PASSWORD:", os.getenv("DB_PASSWORD"))
print("HOST:", os.getenv("DB_HOST"))
print("PORT:", os.getenv("DB_PORT"))
print("NAME:", os.getenv("DB_NAME"))

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DB_URL = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

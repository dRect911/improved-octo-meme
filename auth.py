# auth.py

from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from databases import Database

DATABASE_URL = "sqlite:///./users.db"

engine = create_engine(DATABASE_URL)
metadata = MetaData()

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String, unique=True, index=True),
    Column("hashed_password", String),
)

user_database = Database(DATABASE_URL)

# Autres fonctions pour la gestion de la base de données
# Par exemple, la fonction pour enregistrer un nouvel utilisateur
# def create_user(user: UserCreate, db: Database):
#     ...

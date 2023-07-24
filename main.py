from models import Contact, Entreprise, ContactDB, EntrepriseDB, UserCreate, UserDB
# from auth import users
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from passlib.context import CryptContext
import databases
import sqlalchemy
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from typing import List

app = FastAPI()

DATABASE_URL = "sqlite:///./contacts.db"
USER_DATABASE_URL = "sqlite:///./users.db"
database = databases.Database(DATABASE_URL)
user_database = databases.Database(USER_DATABASE_URL)
metadata = sqlalchemy.MetaData()

Base = declarative_base()

engine = create_engine(DATABASE_URL)


users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String, unique=True, index=True),
    Column("hashed_password", String),
)

user_engine = create_engine(USER_DATABASE_URL)
users.create(bind=user_engine, checkfirst=True)

Base.metadata.create_all(bind=engine)

def get_session():
    with sessionmaker(bind=engine)() as session:
        yield session


@app.post("/contacts/", status_code=status.HTTP_201_CREATED)
async def create_contact(contact: Contact, db: databases.Database = Depends(get_session)):
    contact_db = ContactDB(**contact.dict())
    db.add(contact_db)
    db.commit()
    return contact_db

@app.get("/contacts/", response_model=list[ContactDB])
async def get_contacts(skip: int = 0, limit: int = 10, db: databases.Database = Depends(get_session)):
    return db.query(ContactDB).offset(skip).limit(limit).all()

@app.get("/contact/{contact_id}/", response_model=ContactDB)
async def get_contact(contact_id: int, db: databases.Database = Depends(get_session)):
    contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact

@app.put("/contact/{contact_id}/", response_model=ContactDB)
async def update_contact(contact_id: int, contact: Contact, db: databases.Database = Depends(get_session)):
    existing_contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    if not existing_contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    for key, value in contact.dict().items():
        setattr(existing_contact, key, value)
    
    db.commit()
    return existing_contact

@app.delete("/contact/{contact_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contact_id: int, db: databases.Database = Depends(get_session)):
    contact = db.query(ContactDB).filter(ContactDB.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    db.delete(contact)
    db.commit()
    return


@app.post("/entreprises/", status_code=status.HTTP_201_CREATED)
async def create_entreprise(entreprise: Entreprise, db: databases.Database = Depends(get_session)):
    entreprise_db = EntrepriseDB(**entreprise.dict())
    db.add(entreprise_db)
    db.commit()
    return entreprise_db

@app.get("/entreprises/", response_model=list[EntrepriseDB])
async def get_entreprises(skip: int = 0, limit: int = 10, db: databases.Database = Depends(get_session)):
    return db.query(EntrepriseDB).offset(skip).limit(limit).all()

@app.get("/entreprise/{entreprise_id}/", response_model=EntrepriseDB)
async def get_entreprise(entreprise_id: int, db: databases.Database = Depends(get_session)):
    entreprise = db.query(EntrepriseDB).filter(EntrepriseDB.id == entreprise_id).first()
    if not entreprise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entreprise not found")
    return entreprise

@app.put("/entreprise/{entreprise_id}/", response_model=EntrepriseDB)
async def update_entreprise(entreprise_id: int, entreprise: Entreprise, db: databases.Database = Depends(get_session)):
    existing_entreprise = db.query(EntrepriseDB).filter(EntrepriseDB.id == entreprise_id).first()
    if not existing_entreprise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entreprise not found")

    for key, value in entreprise.dict().items():
        setattr(existing_entreprise, key, value)
    
    db.commit()
    return existing_entreprise

@app.delete("/entreprise/{entreprise_id}/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entreprise(entreprise_id: int, db: databases.Database = Depends(get_session)):
    entreprise = db.query(EntrepriseDB).filter(EntrepriseDB.id == entreprise_id).first()
    if not entreprise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Entreprise not found")
    db.delete(entreprise)
    db.commit()
    return


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# def get_password_hash(password: str):
#     return pwd_context.hash(password)

# @app.post("/register/", response_model=UserDB)
# async def register_user(user: UserCreate, db: user_database):
#     hashed_password = get_password_hash(user.password)
#     query = users.insert().values(username=user.username, hashed_password=hashed_password)
#     return await db.execute(query)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str):
    return pwd_context.hash(password)

def create_user(user: UserCreate, db: user_database):
    hashed_password = get_password_hash(user.password)
    query = users.insert().values(username=user.username, hashed_password=hashed_password)
    return db.execute(query)

@app.post("/register/", response_model=UserDB)
async def register_user(user: UserCreate, db: user_database = Depends(get_session)):
    user_id = await create_user(user, db)
    return {"id": user_id, "username": user.username, "password": "**********"}

    
security = HTTPBasic()

@app.post("/login/")
async def login(credentials: HTTPBasicCredentials = Depends(security)):
    user = await get_user_by_username(credentials.username, db)  # Remplacez cette fonction par celle pour récupérer l'utilisateur par son nom d'utilisateur depuis la base de données

    if user is None or not verify_password(credentials.password, user.hashed_password):  # Remplacez cette fonction par celle pour vérifier le mot de passe avec le mot de passe haché stocké dans la base de données
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Ici, vous pouvez générer un token d'authentification pour l'utilisateur et le renvoyer en réponse
    token = generate_authentication_token(user.username)

    return {"token": token}
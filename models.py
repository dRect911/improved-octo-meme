from pydantic import BaseModel

class Contact(BaseModel):
    nom: str
    prenom: str
    telephone: str
    adresse: str
    email: str

class Entreprise(BaseModel):
    nom: str
    adresse: str
    telephone: str
    secteur_activite: str

class ContactDB(BaseModel):
    id: int
    nom: str
    prenom: str
    telephone: str
    adresse: str
    email: str

    class Config:
        orm_mode = True

class EntrepriseDB(BaseModel):
    id: int
    nom: str
    adresse: str
    telephone: str
    secteur_activite: str

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    password: str

class UserDB(BaseModel):
    id: int
    username: str
    password: str

    class Config:
        orm_mode = True

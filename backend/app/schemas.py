from pydantic import BaseModel
from typing import Optional, List

# Schémas pour Module
class ModuleBase(BaseModel):
    titre: str
    description: str

class ModuleCreate(ModuleBase):
    pass

class Module(ModuleBase):
    id: int
    
    class Config:
        from_attributes = True

# Schémas pour Cours
class CoursBase(BaseModel):
    titre: str
    description: str
    contenu: str
    id_module: Optional[int] = None

class CoursCreate(CoursBase):
    pass

class Cours(CoursBase):
    id: int
    
    class Config:
        from_attributes = True

# Schémas pour Page
class PageBase(BaseModel):
    description: Optional[str] = None
    medias: Optional[str] = ""
    est_vue: Optional[int] = 0
    id_cours: int

class PageCreate(PageBase):
    pass

class Page(PageBase):
    id: int
    
    class Config:
        from_attributes = True

# Schémas pour QCM
class QCMBase(BaseModel):
    question: str
    rep1: str
    rep2: str
    rep3: str
    rep4: str
    soluce: int
    id_cours: int

class QCMCreate(QCMBase):
    pass

class QCM(QCMBase):
    id: int
    
    class Config:
        from_attributes = True



class TextATrueOut(BaseModel):
    id: int
    texte: str
    reponse1: str
    reponse2: str
    reponse3: str
    reponse4: str
    numero_reponse_correcte: int
    explication: Optional[str] = None
    id_cours: int

    class Config:
        from_attributes = True

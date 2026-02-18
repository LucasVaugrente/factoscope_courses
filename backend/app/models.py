from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from .database import Base

class Module(Base):
    __tablename__ = "module"
    
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Relations
    cours = relationship("Cours", back_populates="module")

class Cours(Base):
    __tablename__ = "cours"
    
    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    contenu = Column(String(255), nullable=False)
    id_module = Column(Integer, ForeignKey("module.id", ondelete="CASCADE", onupdate="CASCADE"))
    
    # Relations
    module = relationship("Module", back_populates="cours")
    pages = relationship("Page", back_populates="cours", cascade="all, delete-orphan")
    qcms = relationship("QCM", back_populates="cours", cascade="all, delete-orphan")
    text_a_trou = relationship("TextATrue", back_populates="cours", cascade="all, delete-orphan")

class Page(Base):
    __tablename__ = "page"
    
    id = Column(Integer, primary_key=True, index=True)
    description = Column(Text)
    medias = Column(Text, default="")
    est_vue = Column(Integer, default=0)
    id_cours = Column(Integer, ForeignKey("cours.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    
    # Relations
    cours = relationship("Cours", back_populates="pages")

class QCM(Base):
    __tablename__ = "qcm"
    
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String(255), nullable=False)
    rep1 = Column(String(255), nullable=False)
    rep2 = Column(String(255), nullable=False)
    rep3 = Column(String(255), nullable=False)
    rep4 = Column(String(255), nullable=False)
    soluce = Column(Integer, nullable=False)
    id_cours = Column(Integer, ForeignKey("cours.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    
    # Relations
    cours = relationship("Cours", back_populates="qcms")

class TextATrue(Base):
    __tablename__ = "text_a_trou"
    
    id = Column(Integer, primary_key=True, index=True)
    texte = Column(Text, nullable=False)
    reponse1 = Column(String(255), nullable=False)
    reponse2 = Column(String(255), nullable=False)
    reponse3 = Column(String(255), nullable=False)
    reponse4 = Column(String(255), nullable=False)
    numero_reponse_correcte = Column(Integer, nullable=False)  # 1, 2, 3 ou 4
    explication = Column(Text)
    id_cours = Column(Integer, ForeignKey("cours.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    
    # Relations
    cours = relationship("Cours", back_populates="text_a_trou")

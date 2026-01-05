from sqlalchemy import Column, Integer, String, Text, ForeignKey
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

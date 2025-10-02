from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
import hashlib

Base = declarative_base()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True)
    source = Column(String(50), nullable=False)
    title = Column(String(512), nullable=False)
    url = Column(String(1024), nullable=False)
    published_at = Column(DateTime, nullable=True)
    summary = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    lang = Column(String(10), nullable=True)
    risk_level = Column(String(10), nullable=True)
    impact_direct = Column(Boolean, default=False)
    impact_indirect = Column(Boolean, default=False)
    processed = Column(Boolean, default=False)
    fingerprint = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('fingerprint', name='uq_items_fingerprint'),)

def make_fingerprint(source: str, title: str, url: str) -> str:
    import hashlib
    return hashlib.sha256(f"{source}|{title}|{url}".encode("utf-8")).hexdigest()

def get_session(database_url: str):
    engine = create_engine(database_url, echo=False, future=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

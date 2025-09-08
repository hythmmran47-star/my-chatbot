from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:@localhost/chatbot_db"
SQLALCHEMY_DATABASE_URL = "sqlite:///./filename.sqlite3"


# محرك الاتصال مع خاصية pool_pre_ping لتجنب مشاكل الانقطاع
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

# Session لعمليات DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base لوراثة نماذج SQLAlchemy
Base = declarative_base()

import datetime
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, ForeignKey, Enum, Double, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import enum

# Connection URL
DB_URL = 'postgresql://postgres:postgres@localhost/RealityApplicationDatabase'

# Create an engine and base class
engine = create_engine(DB_URL)
Base = declarative_base()

# Create a session factory
SessionLocal = sessionmaker(bind=engine)

class UserRole(enum.Enum):
    admin = "admin"
    user = "user"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username =  Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), nullable=False)



class Property(Base):
    __tablename__ = 'properties'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    property_id = Column(String(50), nullable=True)
    title = Column(String, nullable=True, default=None)
    description = Column(Text, nullable=True, default=None)
    price = Column(Double, nullable=False, default=0.0)
    price_per_meter = Column(Double, nullable=True, default=None)
    area = Column(Float, nullable=False, default=0.0)
    street = Column(String, nullable=True, default=None)
    city = Column(String, nullable=True, default=None)
    district = Column(String, nullable=True, default=None)
    affiliation = Column(String, nullable=True, default=None)
    typeApt = Column(String, nullable=True, default=None)
    rooms = Column(String, nullable=False, default="1")
    url = Column(Text, nullable=True, default=None)
    category = Column(String, nullable=True, default=None)
    address = Column(String, nullable=True, default=None)
    latitude = Column(Double, nullable=True, default=None)
    longitude = Column(Double, nullable=True, default=None)
    tipped = Column(Boolean, default=False)
    website = Column(String, nullable=True, default=None)
    published_date = Column(Date, nullable=False, default=datetime.date.today)
    parsed = Column(Boolean, default=False)
    typeOfSale = Column(String, nullable=True, default=None)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True, default=1)
    
Base.metadata.create_all(engine)

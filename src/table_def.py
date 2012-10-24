# table_def.py
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///hrm_data.db', echo=True)
Base = declarative_base()
 
########################################################################
class User(Base):
    """"""
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    name = Column(String,unique=True)  
 
    #----------------------------------------------------------------------
    def __init__(self, name):
        """"""
        self.name = name    

    def __repr__(self):
        return "<User('%s')>" % self.name
 
########################################################################
class HeartRateData(Base):
    """"""
    __tablename__ = "heartrate"
 
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    heart_rate = Column(Integer)
    
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", backref=backref("heartrate", order_by=id))
 
    #----------------------------------------------------------------------
    def __init__(self, timestamp, heart_rate):
        """"""
        self.timestamp = timestamp
        self.heart_rate = heart_rate

    def __repr__(self):
        return "<HeartRateData('time: %s, heart-rate %s ')>" % (self.timestamp, self.heart_rate)
 
# create tables
Base.metadata.create_all(engine)

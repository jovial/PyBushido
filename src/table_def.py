#    
#    Copyright (c) 2012, Will Szumski
#    Copyright (c) 2012, Doug Szumski
#
#    This file is part of PyBushido.
#
#    PyBushido is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Foobar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with PyBushido.  If not, see <http://www.gnu.org/licenses/>.
#
#

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

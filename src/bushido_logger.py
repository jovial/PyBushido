#from datetime import datetime
#from sqlalchemy import create_engine
#from sqlalchemy.orm import sessionmaker
#from table_def import User, HeartRateData
#import sys

from bushido import Bushido, BushidoListener

from ant.core import message

#DATABASE = 'hrm_data.db'

#class HrmDatabaseInterface(object):
#    def persist(self,name,hr):
#        raise NotImplementedError()

class BushidoLoggerInterface(object):
    def logSpeed(self,value, time):
        raise NotImplementedError()
    def logHeartRate(self,value, time):
        raise NotImplementedError()
    def logPower(self,value, time):
        raise NotImplementedError()
    def logCadence(self,value, time):
        raise NotImplementedError()
    def logDistance(self,value, time):
        raise NotImplementedError()

class BushidoPrinter(BushidoLoggerInterface):
    def logSpeed(self,value, time):
        print "Speed: ", value
    def logHeartRate(self,value, time):
        print "Heart Rate: ", value
    def logPower(self,value, time):
        print "Power: ", value
    def logCadence(self,value, time):
        print "Cadence: ", value
    def logDistance(self,value, time):
        print "Distance: ", value

#class HrmLogger(object):
#    def __init__(self,name,database):
#        self.name = name
#        self.database = database
#
#    def log(self,hr):
#        database.persist(name,hr)
#
#class DatabaseException(Exception):
#    pass       
#
#class HrmDatabase(HrmDatabaseInterface):
#   
#    engine = create_engine('sqlite:///' + DATABASE, echo=False)
#    Session = sessionmaker(bind=engine)
#
#    def persist(self,name, hr):
#        session = self.Session()
#        user = session.query(User).filter_by(name=name).first()
#        # if user doesn't exist
#        if not user:
#            user = User(name)
#            session.add(user)
#        user.heartrate.append(HeartRateData(datetime.now(),hr))
#        session.commit()
#
#    def getDataInRange(self,name,start,end):           
#        session = self.Session()
#        qry = session.query(User, HeartRateData)
#        qry = qry.filter(User.id==HeartRateData.user_id)
#        qry = qry.filter(User.name==name)
#        #    raise DatabaseException('No user by that name comes about these parts')
#        print start, end
#        data = qry.filter(HeartRateData.timestamp.between(start, end)).all()
#        timestamps = []
#        hr = []
#        if not data:
#            return timestamps, hr
#        for user, hrmData in data:
#            timestamps.append(hrmData.timestamp)
#            hr.append(hrmData.heart_rate)
#        return timestamps , hr
        
if __name__ == "__main__":
               
#    if len(sys.argv) < 2:
#        raise ValueError("Need to specify a username") 
#    name = sys.argv[1]
#    database = HrmDatabase()
    #logger = HrmLogger(name,database)
    logger = BushidoPrinter()
    bushido = Bushido(logger,period=5)
    bushido.start()
 




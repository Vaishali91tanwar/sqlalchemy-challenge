import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, and_

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """Lists all available api routes."""
    return (
        f"Welcome to the home page!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate/2017-08-03<br/>"
        f"/api/v1.0/startdate/2016-08-09/enddate/2017-01-01<br/>"
    )


@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return dictionary of all precipiation values with date as key"""
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Create a dictionary with date as akey and prcp as value
    prcp_list = []
    prcp_dict={}
    for date, prcp in results:
        if date  not in prcp_dict:
            prcp_dict[date] = [prcp]
        elif date in prcp_dict:
            (prcp_dict[date]).append(prcp)
    
    return jsonify(prcp_dict)

@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    # Query all stations
    results = session.query(Station.name).all()

    session.close()

    # Convert list of tuples into normal list
    station_names = list(np.ravel(results))

    return jsonify(station_names)


@app.route("/api/v1.0/tobs")
def tobs():
     session=Session(engine)

     #Query to find the most active station 
     counts=session.query(Measurement.station,Station.name,func.count(Measurement.tobs)).join(Station,\
     Measurement.station == Station.station).group_by(Measurement.station).\
     order_by(func.count(Measurement.tobs).desc()).first()
     
     
    #Most active station details  
     (id, name, count)=np.ravel(counts)

    #Query to get the dates and temperature observations for the last year of data
     last_year=session.query(Measurement.date,Measurement.tobs).filter(Measurement.station==id).filter(func.strftime("%Y",Measurement.date)=="2017").all()

     print(f"The most active station is: {name} with id: {id} and count: {count}")
     #Query to get the temperature observations for last year of data for most active station
     results=session.query(Measurement.tobs).filter(Measurement.station==id).filter(func.strftime("%Y",Measurement.date)=="2017").all()
     session.close()
     tobs_data= list(np.ravel(results))
     return jsonify(tobs_data)


@app.route("/api/v1.0/startdate/<startdate>")
def analysis(startdate):
    session=Session(engine)

    #Query to find out temp statistics for a given start date
    results=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(Measurement.date>=startdate).all()
    session.close()

    (minT,maxT,avgT)=list(np.ravel(results))
    #Storing in a dictionary
    stats_dict={"Min Temp":minT,"Max Temp":maxT,"Avg Temp":avgT}
    return jsonify(stats_dict)
    
@app.route("/api/v1.0/startdate/<startdate>/enddate/<enddate>")
def analysis_2(startdate,enddate):
    session=Session(engine)
    #Query to find out the temp statistics for a given start and end date
    results=session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
    filter(and_(Measurement.date>=startdate, Measurement.date<=enddate)).all()
    
    session.close()
    
    (minT,maxT,avgT)=list(np.ravel(results))
    #Storing results in a dictionary
    stats_dict={"Min Temp":minT,"Max Temp":maxT,"Avg Temp":avgT}
    return jsonify(stats_dict)
    



if __name__ == '__main__':
    app.run(debug=True)

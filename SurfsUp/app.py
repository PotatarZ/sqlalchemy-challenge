import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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
Station = Base.classes.station


#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start_date YYYY-MM-DD)<br/>"
        f"/api/v1.0/(start_date YYYY-MM-DD)/(end_date YYYY-MM-DD)"
    )


@app.route("/precipitation")
def precipitation():
    """Query the DB for records of the last year and return a json"""
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    all_dates = session.query(Measurement.date).all()
    most_recent = max(all_dates)

    # Calculate the date one year from the last date in data set.
    most_recent_dt = dt.datetime.strptime(most_recent[0], '%Y-%m-%d').date()
    lower_date = most_recent_dt - dt.timedelta(days=365)

    # Perform a query to retrieve the recent data's dates and prcp scores
    recent_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= lower_date).all()

    session.close()

    # Create a dictionary with dates as keys and prcp as values
    prcp_dict = {}
    for date, prcp in recent_data:
        prcp_dict[date] = prcp

    return jsonify(prcp_dict)


@app.route("/stations")
def stations():
    """Returns all stations as a jsonified list"""
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Get all stations from the Station table
    stations_list = session.query(Station.station).all()

    session.close()

    return jsonify(list(np.ravel(stations_list)))


@app.route("/tobs")
def tobs():
    """Returns recent temperature observations for the most active station"""
    # Create a session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set
    all_dates = session.query(Measurement.date).all()
    most_recent = max(all_dates)

    # Calculate the date one year from the last date in data set
    most_recent_dt = dt.datetime.strptime(most_recent[0], '%Y-%m-%d').date()
    lower_date = most_recent_dt - dt.timedelta(days=365)

    # Find the name of the most active station during the last year
    most_active = session.query(Measurement.station, func.count(Measurement.id)).\
        filter(Measurement.date >= lower_date).\
        group_by('station').\
        order_by(func.count(Measurement.id).desc()).first()[0]

    # Perform a query to retrieve the recent tobs scores from the most active station
    recent_temps = session.query(Measurement.tobs).\
        filter(Measurement.date >= lower_date).\
        filter(Measurement.station == most_active).all()

    session.close()

    return(jsonify(list(np.ravel(recent_temps))))


@app.route("/<start>")
def start(start):
    """Find the max, min, and avg temps recorded from start_date"""
    # Create a session (link) from Python to the DB
    session = Session(engine)

    max_temp = session.query(func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).first()[0]
    
    min_temp = session.query(func.min(Measurement.tobs)).\
              filter(Measurement.date >= start).first()[0]
    
    avg_temp = session.query(func.avg(Measurement.tobs)).\
              filter(Measurement.date >= start).first()[0]
    
    session.close()
    
    return jsonify({'start_date':start},
                   {'results':{'max':max_temp, 'min':min_temp, 'avg':avg_temp}})


@app.route("/<start>/<end>")
def start_end(start, end):
    """Find the max, min, and avg temps recorded from start_date to end_date"""
    # Create a session (link) from Python to the DB
    session = Session(engine)

    max_temp = session.query(func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              filter(Measurement.date <= end).first()[0]
    
    min_temp = session.query(func.min(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              filter(Measurement.date <= end).first()[0]
    
    avg_temp = session.query(func.avg(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              filter(Measurement.date <= end).first()[0]
    
    session.close()
    
    return jsonify({'start_date':start, 'end_date':end},
                   {'results':{'max':max_temp, 'min':min_temp, 'avg':avg_temp}})


#################################################
# Main
#################################################

if __name__ == '__main__':
    app.run(debug=True)
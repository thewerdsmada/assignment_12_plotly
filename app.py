#LIBRARY CARDS
import os
import pandas as pd
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


#Connect to the database

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get('DATABASE_URL', '') or "sqlite:///db/bellybutton.sqlite"
db = SQLAlchemy(app)

# mirror mirror on the wall
base = automap_base()
# who's got the copied downest database of all
base.prepare(db.engine, reflect=True)

# Save references to each table
Samples_Metadata = base.classes.sample_metadata
Samples = base.classes.samples

#Make some webpages, first do the index
@app.route("/")
def index():
    return render_template("index.html")

#make a page that lists the sample names
@app.route("/names")
def names():
    # UNLEASH THE PANDAS
    stmt = db.session.query(Samples).statement
    belly_button_df = pd.read_sql_query(stmt, db.session.bind)

    # Halloween the pandas
    return jsonify(list(belly_button_df.columns)[2:])

#zoom in on a particular sample
@app.route("/metadata/<sample>")
def sample_metadata(sample):
    sel = [
        Samples_Metadata.sample,
        Samples_Metadata.ETHNICITY,
        Samples_Metadata.GENDER,
        Samples_Metadata.AGE,
        Samples_Metadata.LOCATION,
        Samples_Metadata.BBTYPE,
        Samples_Metadata.WFREQ,
    ]

    results = db.session.query(*sel).filter(Samples_Metadata.sample == sample).all()

    # miriam webster that stuff
    sample_metadata = {}
    for result in results:
        sample_metadata["sample"] = result[0]
        sample_metadata["ETHNICITY"] = result[1]
        sample_metadata["GENDER"] = result[2]
        sample_metadata["AGE"] = result[3]
        sample_metadata["LOCATION"] = result[4]
        sample_metadata["BBTYPE"] = result[5]
        sample_metadata["WFREQ"] = result[6]

    print(sample_metadata)

    #send me back some halloween action
    return jsonify(sample_metadata)


@app.route("/samples/<sample>")
def samples(sample):
    """Return `otu_ids`, `otu_labels`,and `sample_values`."""
    stmt = db.session.query(Samples).statement
    belly_button_sample_df = pd.read_sql_query(stmt, db.session.bind)


    # BRITA out the small particulate matter from the water......
    sample_data = belly_button_sample_df.loc[belly_button_sample_df[sample] > 1, ["otu_id", "otu_label", sample]]
    sample_data.sort_values(by=sample, inplace=True, ascending=False)
    # housekeeping
    data = {
        "otu_ids": sample_data.otu_id.values.tolist(),
        "sample_values": sample_data[sample].values.tolist(),
        "otu_labels": sample_data.otu_label.tolist(),
    }
    #dissonant piano music with some cool 80's synths 
    return jsonify(data)


if __name__ == "__main__":
    app.run(debug=True)
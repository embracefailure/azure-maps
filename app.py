import os, json
from flask import Flask, request, render_template
import requests

#Load the Azure maps key from the environment.env file
MAP_KEY=os.environ["MAP_KEY"]
WAQI_API_KEY=os.environ["WAQI_API_KEY"]
WAQI_API_URL="https://api.waqi.info/map/bounds/?latlng={},{},{},{}&token={}"
#initiate the Flask app
app = Flask(__name__)

#Handle requests to the root of the website, returning the home page 
@app.route('/')
def home():
    #create data for the home page to pass the Maps key 
    data = {"map_key": MAP_KEY}
    #return the rendered HTML page
    return render_template('home.html', data=data)

def get_color(aqi):
    # convert the aqi value to a color
    if aqi <= 50: return "#009966"
    if aqi<=100:return "#ffde33"
    if aqi<=150:return "#ff9933"
    if aqi<=200:return "#cc0033"
    if aqi<=300:return "#660099"
    return "#7e0023"

def load_aqi_data(lon1, lat1, lon2, lat2):
    # Load the air quality data.
    url = WAQI_API_URL.format(lat1, lon1, lat2, lon2, WAQI_API_KEY)
    aqi_data=requests.get(url)

    # Create a GeoJSON feature collection from the data.
    feature_collection={
        "type": "FeatureCollection",
        "features": []
    }

    for value in aqi_data.json()["data"]:
        # filter out empty values
        if value["aqi"] !="-":
            feature_collection["features"].append({
                "type": "Feature",
                "properties": {
                    "color": get_color(int(value["aqi"]))
            },
            "geometry": {
                "type": "Point",
                "coordinates": [value["lon"], value["lat"]]
                }
                })
    return feature_collection

@app.route('/aqi',methods=["GET"])
def get_aqi():
    # get the bounds from the request
    bounds=request.args["bounds"].split(",")

    # load the AQI data and create the GeoJSON for the specified bounds
    return json.dumps(load_aqi_data(bounds[0], bounds[1], bounds[2], bounds[3]))

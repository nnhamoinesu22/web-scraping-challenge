# Import Dependencies 
from flask import Flask,render_template, redirect 
from flask_pymongo import PyMongo
import os
import  scrape_mars 


# Create an instance of Flask app
app = Flask(__name__)

# Use flask_pymongo to set up mongo connection locally 
app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)


# Create route that renders index.html template and finds documents from mongo
@app.route("/")
def index(): 

    # Find data
    mars_info_dict = mongo.db.mars.find_one()

    # Return template and data
    return render_template("index.html", mars_info_dict=mars_info_dict)

# Route that will trigger scrape function
@app.route("/scrape")
def scrape(): 

    # Run scrapped functions
    #mars_info_dict = mongo.db.mars
    mars_data = scrape_mars.scrape_info()
    mars_info_dict.update({}, mars_data, upsert=True)

    return redirect("/", code=302)

if __name__ == "__main__": 
    app.run(debug= True)
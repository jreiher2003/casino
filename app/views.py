from app import app
from flask import render_template
from app.utils import connect_mongo, connect_mongo_gwages

db = connect_mongo()
gwages = connect_mongo_gwages()

@app.route("/")
def index():
    blog = db.find()
    gwages1 = gwages.find()
    return render_template(
        "index.html", 
        blog=blog,
        gwages=gwages1
        )
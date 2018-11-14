from flask import Flask, jsonify, request
from pymodm import MongoModel, fields, connect
import datetime

connect("mongodb://av135:Dukebm3^@ds039778.mlab.com:39778/hr_sentinel")

class User(MongoModel):
    mrn = fields.CharField(primary_key=True)
    attending_email = fields.EmailField()
    user_age = fields.IntegerField()
    heart_rate = fields.ListField()
    heart_rate_timestamp = fields.ListField()

def istachycardic(user_age, hr):

    if user_age > 5475/365:
        tachy_threshold = 100
    elif user_age > 4015/365:
        tachy_threshold = 119
    elif user_age > 2555/365:
        tachy_threshold = 130
    elif user_age > 1460/365:
        tachy_threshold = 133
    elif user_age > 730/365:
        tachy_threshold = 137
    elif user_age > 335/365:
        tachy_threshold = 151
    elif user_age > 152/365:
        tachy_threshold = 169
    elif user_age > 61/365:
        tachy_threshold = 186
    elif user_age > 21/365:
        tachy_threshold = 179
    elif user_age > 6/365:
        tachy_threshold = 182
    elif user_age > 2/365:
        tachy_threshold = 166
    elif user_age > 0:
        tachy_threshold = 159

    if hr > tachy_threshold:
        return True
    else:
        return False

app = Flask(__name__)

@app.route("/", methods=["GET"])
def greeting():
    """
    Returns the string "Welcome to the heart rate sentinel"
     to the caller
    """
    return "Welcome to the heart rate sentinel"




@app.route("/data", methods=["GET"])
def getData():
    """
    Returns the data dictionary below to the caller as JSON
    """
    first_user = User.objects.raw({"_id": "123"}).first()
    dict_array = {"patient_id": first_user.mrn,
                  "attending_email": first_user.attending_email,
                  "user_age": first_user.user_age,
                  "heart_rate": first_user.heart_rate,
                  "heart_rate_timestamp": first_user.heart_rate_timestamp
                  }
    return jsonify(dict_array)

@app.route("/heart_rate", methods=["POST"])
def addHr():
    data_in = request.get_json()
    u = User.objects.raw({"_id": data_in["patient_id"]}).first()
    u.heart_rate.append(data_in["heart_rate"])
    currenttime = datetime.datetime.now().time()
    u.heart_rate_timestamp.append(currenttime.isoformat())
    u.save()
    return u.mrn

@app.route("/new_patient", methods=["POST"])
def addpatient():
    now = datetime.datetime.now().time()
    data_in = request.get_json()
    u = User(mrn=data_in["patient_id"],
             attending_email=data_in["attending_email"],
             user_age=data_in["user_age"],
             heart_rate=[0],
             heart_rate_timestamp=[now.isoformat()]
             )
    u.save()
    return u.mrn

if __name__ == "__main__":
    app.run(host="0.0.0.0")

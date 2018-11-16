from flask import Flask, jsonify, request
from pymodm import MongoModel, fields, connect
from datetime import datetime
import sendgrid
import numpy as np
from sendgrid.helpers.mail import *

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

def averageHR(hr):
    return sum(hr)/float(len(hr))

app = Flask(__name__)

@app.route("/", methods=["GET"])
def greeting():
    """
    Returns the string "Welcome to the heart rate sentinel"
     to the caller
    """
    return "Welcome to the heart rate sentinel"




@app.route("/data/<patient_id>", methods=["GET"])
def getData(patient_id):
    """ Returns the data dictionary below to the caller as JSON

    This function returns all the stored information for a patient as a JSON dictionary

    Args:
        patient_id (string): string specifying patient MRN.

    Returns:
        dict_array (dict): Dictionary of stored information for specified patient
    """

    u = User.objects.raw({"_id": patient_id}).first()
    dict_array = {"patient_id": u.mrn,
                  "attending_email": u.attending_email,
                  "user_age": u.user_age,
                  "heart_rate": u.heart_rate,
                  "heart_rate_timestamp": u.heart_rate_timestamp
                  }
    return jsonify(dict_array)

@app.route("/status/<patient_id>", methods=["GET"])
def getStatus(patient_id):
    """ Returns whether patient is tachycardic based on previously available data

    This function returns whether the specified patient is currently tachycardic based on previously available
     heart rate data, as well as the timestamp of the most recent heart rate.

    Args:
        patient_id (string): string specifying patient MRN.

    Returns:
        ans (string): Specifying if patient is tachycardic
    """
    u = User.objects.raw({"_id": patient_id}).first()
    most_recent_hr = u.heart_rate[-1]
    most_recent_time = u.heart_rate_timestamp[-1]
    tachy = istachycardic(u.user_age, most_recent_hr)
    ansraw = "Patient is {} His/Her heart rate is {} based on data from {}"
    if tachy:
        ans = ansraw.format("tachycardic!", most_recent_hr, most_recent_time)
        a = email('av135_hr_sentinel@duke.edu', u.attending_email, 'Urgent patient #{}!'.format(u.mrn), ans)
        return ans
    else:
        ans = ansraw.format("not tachycardic.", most_recent_hr, most_recent_time)
        return ans

@app.route("/heart_rate/<patient_id>", methods=["GET"])
def getHR(patient_id):
    """
    Returns the data dictionary below to the caller as JSON
    """
    u = User.objects.raw({"_id": patient_id}).first()
    total_stored_hr_data = u.heart_rate[1:]
    return str(total_stored_hr_data)

@app.route("/heart_rate/average/<patient_id>", methods=["GET"])
def getavgHR(patient_id):
    """
    Returns the data dictionary below to the caller as JSON
    """
    u = User.objects.raw({"_id": patient_id}).first()
    total_stored_hr_data = u.heart_rate[0:]
    avghr = averageHR(total_stored_hr_data)
    ans ="The patient's average heart over all stored measurements is {}."
    return ans.format(avghr)

@app.route("/heart_rate", methods=["POST"])
def addHr():
    data_in = request.get_json()
    u = User.objects.raw({"_id": data_in["patient_id"]}).first()
    u.heart_rate.append(data_in["heart_rate"])
    currenttime = datetime.now()
    u.heart_rate_timestamp.append(currenttime.isoformat())
    if u.heart_rate[0] == 0:   # Removes initialization value
        u.heart_rate.pop(0)
        u.heart_rate_timestamp.pop(0)
    u.save()
    return u.mrn

@app.route("/new_patient", methods=["POST"])
def addpatient():
    now = datetime.now()
    data_in = request.get_json()
    u = User(mrn=data_in["patient_id"],
             attending_email=data_in["attending_email"],
             user_age=data_in["user_age"],
             heart_rate=[0],
             heart_rate_timestamp=[now.isoformat()]
             )
    u.save()
    return u.mrn

@app.route("/heart_rate/interval_average", methods=["POST"])
def intervalaverage():
    data_in = request.get_json()
    u = User.objects.raw({"_id": data_in["patient_id"]}).first()
    hr_since = datetime.strptime(data_in["heart_rate_average_since"], "%Y-%m-%dT%H:%M:%S.%f")# includes data at specified time point
    hr_time_stamp_datetime = [datetime.strptime(i, "%Y-%m-%dT%H:%M:%S.%f") for i in u.heart_rate_timestamp]
    hr_time_stamp_array = np.asarray(hr_time_stamp_datetime)
    hr_array = np.asarray(u.heart_rate)
    adjusted_hr_data = recondition(hr_since, hr_time_stamp_array, hr_array)
    avg = averageHR(adjusted_hr_data)
    ans ="The patient's average heart since {} is {}."
    return ans.format(data_in["heart_rate_average_since"], avg)

def email(from_email_string, to_email_string, subject, content_string):
    key = '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'
    sg = sendgrid.SendGridAPIClient(apikey=key)
    from_email = Email(from_email_string)
    to_email = Email(to_email_string)
    content = Content("text/plain", content_string)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    return response.status_code

def recondition(heart_rate_average_since, heart_rate_timestamp, heart_rate):
    relevant_indices = (heart_rate_timestamp >= heart_rate_average_since).nonzero()
    reconditioned_hr_data = heart_rate[relevant_indices].tolist()
    return reconditioned_hr_data





if __name__ == "__main__":
    app.run(host="0.0.0.0")

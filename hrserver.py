from flask import Flask, jsonify, request
from pymodm import MongoModel, fields, connect
from datetime import datetime
import sendgrid
import numpy as np
from sendgrid.helpers.mail import *
import logging
logging.basicConfig(filename='log.txt', level=logging.DEBUG)

connect("mongodb://av135:Dukebm3^@ds039778.mlab.com:39778/hr_sentinel")

class User(MongoModel):
    """ This User class initializes the MongoDB database attributes

    This class specifies the stored data fields for the heart rate sentinel database.

    Attributes:
        mrn (string): string specifying patient MRN.
        attending_email (email): Specifies patient's attending physician's email.
        user_age (float): Specifies patient's age in years.
        heart_rate (list): Contains all the stored heart rate data
        heart_rate_timestamp (list): Contains associated timestamps of heart_rate data

    """

    mrn = fields.CharField(primary_key=True)
    attending_email = fields.EmailField()
    user_age = fields.FloatField()
    heart_rate = fields.ListField()
    heart_rate_timestamp = fields.ListField()


app = Flask(__name__)

@app.route("/", methods=["GET"])
def greeting():
    """ Welcomes user to heart rate sentinel

    This function returns the following string: "Welcome to the heart rate sentinel"
    Returns:
        welcome (string): "Welcome to the heart rate sentinel"
    """

    welcome = "Welcome to the heart rate sentinel"
    return welcome





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
     heart rate data, as well as the timestamp of the most recent heart rate. Furthermore, it also sends an
     email to the attending physician if the patient is tachycardic.

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
        logging.debug('Tachycardia!')
        return ans
    else:
        ans = ansraw.format("not tachycardic.", most_recent_hr, most_recent_time)
        logging.debug('No tachycardia.')
        return ans

@app.route("/heart_rate/<patient_id>", methods=["GET"])
def getHR(patient_id):
    """ Returns all the stored heart rate data for a specified patient

    This function returns all the previously stored heart rate data as a string
    for a specified patient.

    Args:
        patient_id (string): string specifying patient MRN.

    Returns:
        total_stored_hr_data (str): Contains all the stored heart rate data
    """

    u = User.objects.raw({"_id": patient_id}).first()
    total_stored_hr_data = u.heart_rate[0:]
    logging.debug('The total heart rate data:{}'.format(total_stored_hr_data))
    return str(total_stored_hr_data)

@app.route("/heart_rate/average/<patient_id>", methods=["GET"])
def getavgHR(patient_id):
    """ Returns an average of all the stored heart rate data for a specified patient

    This function returns an average of all the stored heart rate
     data for a specified patient

    Args:
        patient_id (string): string specifying patient MRN.

    Returns:
        ans (str): sentence that informs user of patients average heart rate
    """

    u = User.objects.raw({"_id": patient_id}).first()
    total_stored_hr_data = u.heart_rate[0:]
    avghr = averageHR(total_stored_hr_data)
    ans ="The patient's average heart rate over all stored measurements is {}."
    logging.debug(ans.format(avghr))
    return ans.format(avghr)

@app.route("/heart_rate", methods=["POST"])
def addHr():
    """ Posts heart rate data to database and checks for tachycardia

    This function receives a JSON request and posts the new data to the specified patient's
     heart rate data. It also checks for tachycardia, and emails the physician if
      tachycardia is detected. The function returns a string explaining the most recent
       heart rate status of the patient. Furthermore, it removes the initialized heart rate value
       (0) and associated time stamp.


    Args:
        patient_id (string): string specifying patient MRN (received through JSON request).

    Returns:
        status (str): sentence that informs user of patients recent heart rate status
    """

    data_in = request.get_json()
    required_hr_keys = [
        "patient_id",
        "heart_rate"
    ]
    for key in required_hr_keys:
        if key not in data_in.keys():
            raise ValueError("Key '{}' is missing to post patient heart rate data in sentinel".format(key))

    u = User.objects.raw({"_id": data_in["patient_id"]}).first()
    u.heart_rate.append(data_in["heart_rate"])
    currenttime = datetime.now()
    u.heart_rate_timestamp.append(currenttime.isoformat())
    if u.heart_rate[0] == 0:   # Removes initialization value
        u.heart_rate.pop(0)
        u.heart_rate_timestamp.pop(0)
    logging.debug('Heart rate data was successfully saved for patient #{}'.format(u.mrn))
    u.save()
    status = getStatus(data_in["patient_id"]) # Runs status function to warn if tachycardia is detected
    return status

@app.route("/new_patient", methods=["POST"])
def addpatient():
    """ Initializes database variables for a new patient.

    This function receives a JSON request and initializes the database variables for the new patient.

    Args:
        mrn (string): string specifying patient MRN.
        attending_email (email): Specifies patient's attending physician's email.
        user_age (float): Specifies patient's age in years.
        heart_rate (list): Contains all the stored heart rate data
        heart_rate_timestamp (list): Contains associated timestamps of heart_rate data

    Returns:
        u.mrn (str): identifies patient. No two patients can have the same MRN.
    """

    now = datetime.now()
    data_in = request.get_json()
    required_patient_keys = [
        "patient_id",
        "attending_email",
        "user_age",
    ]
    for key in required_patient_keys:
        if key not in data_in.keys():
            raise ValueError("Key '{}' is missing to initialize patient in sentinel".format(key))
    for i in User.objects.raw():
        if i.mrn == data_in["patient_id"]:
            raise ValueError('This patient is already in the database. Please'
                             'proceed to /api/heart_rate to post heart rate data')

    u = User(mrn=data_in["patient_id"],
             attending_email=data_in["attending_email"],
             user_age=data_in["user_age"],
             heart_rate=[0],
             heart_rate_timestamp=[now.isoformat()]
             )
    logging.debug("Patient #{} was successfully initialized")
    u.save()
    return u.mrn

@app.route("/heart_rate/interval_average", methods=["POST"])
def intervalaverage():
    """ Calculates average of stored heart rates after a specified time point.

    This function calculates the average of the stored heart rates after a
     specified time point.

    Args:
        patient_id (string): string specifying patient MRN (received through JSON request).
        heart_rate_average_since (string): time string to specify time point for interval average.

    Returns:
        u.mrn (str): identifies patient. No two patients can have the same MRN.
    """
    data_in = request.get_json()

    required_patient_keys = [
        "patient_id",
        "heart_rate_average_since"
    ]
    for key in required_patient_keys:
        if key not in data_in.keys():
            raise ValueError("Key '{}' is missing to initialize patient in sentinel".format(key))

    u = User.objects.raw({"_id": data_in["patient_id"]}).first()
    hr_since = datetime.strptime(data_in["heart_rate_average_since"], "%Y-%m-%dT%H:%M:%S.%f")# includes data at specified time point
    hr_time_stamp_datetime = [datetime.strptime(i, "%Y-%m-%dT%H:%M:%S.%f") for i in u.heart_rate_timestamp]
    hr_time_stamp_array = np.asarray(hr_time_stamp_datetime)
    hr_array = np.asarray(u.heart_rate)
    adjusted_hr_data = recondition(hr_since, hr_time_stamp_array, hr_array)
    avg = averageHR(adjusted_hr_data)
    ans ="The patient's average heart since {} is {}."
    logging.debug('Interval average was calculated to be {}.'.format(avg))
    return ans.format(data_in["heart_rate_average_since"], avg)

def email(from_email_string, to_email_string, subject, content_string):
    """ Sends email using SendGrid API

    This function utilizes the SendGrid API to send an email.

    Args:
        from_email_string (string): specifies the email address the message will be sent from.
        to_email_string (string): specifies the email address the message will be sent to.
        subject (string): specifies subject of the email
        content_string (string): specifies the content of the email

    Returns:
        response.status_code (int): code to inform user of email status
    """

    key = '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'
    sg = sendgrid.SendGridAPIClient(apikey=key)
    from_email = Email(from_email_string)
    to_email = Email(to_email_string)
    content = Content("text/plain", content_string)
    mail = Mail(from_email, subject, to_email, content)
    response = sg.client.mail.send.post(request_body=mail.get())
    logging.debug('Email status code: {}'.format(response.status_code))
    return response.status_code

def recondition(heart_rate_average_since, heart_rate_timestamp, heart_rate):
    """ reconditions heart rate list for interval average

    This function compares the specified time point to the timestamps of the
    heart rate data and returns a heart rate vector containing data for the
    interval specified.

    Args:
        heart_rate (array): numpy array of heart rate data.
        heart_rate_average_since (datetime): datetime object for specified interval
        heart_rate_timestamp (array): numpy array of datetimes corresponding to heart rate data

    Returns:
        reconditioned_hr_data (list): list of hr data in specified interval
    """
    relevant_indices = (heart_rate_timestamp >= heart_rate_average_since).nonzero()
    reconditioned_hr_data = heart_rate[relevant_indices].tolist()
    return reconditioned_hr_data

def istachycardic(user_age, hr):
    """ Determines if patient is tachycardic

    This function determines if a patient of a specified age is tachycardic .

    Args:
        user_age (float): patient age in years.
        hr (float): heart rate in beats per minute.

    Returns:
        tachy (boolean): specifies whether patient is tachycardic
    """

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
        tachy = True
    else:
        tachy = False
    return tachy

def averageHR(hr):
    """ Calculates average heart rate.

    This function calculates the average of a list.

    Args:
        hr (list): list of hr data

    Returns:
        avg (float): average heart rate
    """
    
    avg = sum(hr)/float(len(hr))
    return avg




if __name__ == "__main__":
    app.run(host="0.0.0.0")

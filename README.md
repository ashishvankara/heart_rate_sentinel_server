# heart_rate_sentinel_server
Heart Rate Sentinel Assignment 2018 [1.0.0]
## Status badge:
![alt text](https://travis-ci.com/ashishvankara/heart_rate_sentinel_server.svg?branch=master "Status Badge")

## Introduction

The goal of this server is receive POST requests from mock patient heart rate monitors. If a patient exhibits tachycardia , the associated physician receives an email warning. 
The following api routes have been implemented:
* `POST /api/new_patient`: initializes the database variables for a new patient for subsequent heart rate data posts.
  ```sh
  {
      "patient_id": "XXXXXXX", # patient MRN
      "attending_email": "attending_physician@duke.edu", 
      "user_age": 50 # in years
  }
  ```

* `POST /api/heart_rate`: posts heart rate data to database and checks for tachycardia
  ```sh
  {
      "patient_id": "1", # patient MRN
      "heart_rate": 100 # in beats/min
  }
  ``` 

* `POST /api/heart_rate/interval_average`: returns the average of the stored heart rates after a specified time point.
  ```sh
  {
      "patient_id": "1",
      "heart_rate_average_since": "2018-03-09 11:00:36.372339" // date string
  }
  ``` 

* `GET /api/status/<patient_id>` returns whether patient is tachycardic based on the most recent  heart rate, and returns the timestamp of the most recent heart rate. 
* `GET /api/heart_rate/<patient_id>` returns all previous heart rate data. 
* `GET /api/heart_rate/average/<patient_id>` returns the patients's average heart rate over all stored measurements. 
* `GET /api/data/<patient_id>` returns all the stored information for a patient as a JSON dictionary 
  ```sh
  {
      "patient_id": "X",
      "attending_email": "attending_physician@duke.edu", 
      "user_age": X, # in years 
      "heart_rate": X,  # list of heart rate data
      "heart_rate_timestamp": X # list of time stamps 
  }
  ```   


## Code

The software package is separated into the following files: 

- hrserver.py: This script contains all the functions necessary for the server.
- test_hrserver.py: This script contains associated unit testing. 
- getpostsentinel.py: This script functions as a client (or mock heart rate monitor) that interacts with the server. 

See documentation for additional details (\heart_rate_sentinel_server\docs\build\html\index.html)
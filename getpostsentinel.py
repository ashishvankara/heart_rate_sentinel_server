import requests
import datetime

hello = requests.get("http://127.0.0.1:5000/")

# Initialize Patient
r1 = requests.post(
    "http://127.0.0.1:5000/new_patient", json={"patient_id": "123",
                         "attending_email": 'av135@duke.edu',
                         "user_age": 2}
                   )

# Post heart rate (includes status check)
r3 = requests.post(
    "http://127.0.0.1:5000/heart_rate", json={"patient_id": "123",
                                              "heart_rate": 300}
                   )
print(r3.text)
# Check status
r4 = requests.get("http://127.0.0.1:5000/status/123")
print(r4.text)

# Returns HR list; may be [0] if no HR has been posted
r6 = requests.get("http://127.0.0.1:5000/heart_rate/123")
print(r6.text)

# Take time point a
a = datetime.datetime.now()

# Post hr data after time point a
r7 = requests.post(
    "http://127.0.0.1:5000/heart_rate", json={"patient_id": "123",
                                              "heart_rate": 100})
# Take time point b
b = datetime.datetime.now()

# Post hr data after time point b
r8 = requests.post(
    "http://127.0.0.1:5000/heart_rate", json={"patient_id": "123",
                                              "heart_rate": 300})

# Get total hr average (should be 700/3)
r = requests.get("http://127.0.0.1:5000/heart_rate/average/123")
print(r.text)

# Get interval hr average(Can change between a and b time points)

rsince = requests.post(
    "http://127.0.0.1:5000/heart_rate/interval_average", json={"patient_id": "123",
                                                               "heart_rate_average_since": b.isoformat()})
print(rsince.text)

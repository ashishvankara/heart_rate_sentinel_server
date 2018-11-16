import requests
import datetime

hello = requests.get("http://127.0.0.1:5000/")

r1 = requests.post("http://127.0.0.1:5000/new_patient",
                   json={"patient_id": "123",
                         "attending_email": 'av135@duke.edu',
                         "user_age": 2}
                   )

#r2 = requests.get("http://127.0.0.1:5000/data")
#print(r2.json())

r3 = requests.post("http://127.0.0.1:5000/heart_rate",
                   json={"patient_id": "123",
                         "heart_rate": 300})

r4 = requests.get("http://127.0.0.1:5000/status/123")
r4 = requests.get("http://127.0.0.1:5000/data")
print(r4.json())

r5 = requests.get("http://127.0.0.1:5000/status/123")
print(r5.text)

r6 = requests.get("http://127.0.0.1:5000/heart_rate/123")
print(r6.text)

a = datetime.datetime.now()

r7 = requests.post("http://127.0.0.1:5000/heart_rate",
                   json={"patient_id": "123",
                         "heart_rate": 0})
b = datetime.datetime.now()

r8 = requests.post("http://127.0.0.1:5000/heart_rate",
                   json={"patient_id": "123",
                         "heart_rate": 300})

r = requests.get("http://127.0.0.1:5000/heart_rate/average/123")

# Can change between a and b to test interval avg

rsince = requests.post("http://127.0.0.1:5000/heart_rate/interval_average",
                   json={"patient_id": "123",
                         "heart_rate_average_since": a.isoformat()})
print(rsince.text)




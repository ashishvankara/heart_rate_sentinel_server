import requests
#import json

a = requests.get("http://127.0.0.1:5000/")
print(a.text)

r1 = requests.post("http://127.0.0.1:5000/new_patient",
                   json={"patient_id": "123",
                         "attending_email": 'av135@duke.edu',
                         "user_age": 2}
                   )

r2 = requests.get("http://127.0.0.1:5000/data")
print(r2.json())

r3= requests.post("http://127.0.0.1:5000/heart_rate",
                   json={"patient_id": "123",
                         "heart_rate": 65})

r4 = requests.get("http://127.0.0.1:5000/data")
print(r4.json())





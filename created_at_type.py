import json
import requests

response = requests.get("https://nroer.gov.in/api/v1/created_at")
todos = json.loads(response.text)
#print(todos)
with open("created_at.json", "w") as write_file:
    json.dump(todos, write_file,sort_keys=True)
    print('File created')
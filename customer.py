import requests

token = input("Enter AgentGate token: ")

r = requests.post(
    "http://127.0.0.1:8000/api/verify",
    json={
        "secret": "sk_test456",
        "token": token
    }
)

print(r.json())
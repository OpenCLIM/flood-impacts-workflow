import requests
import os

username = os.getenv('DAFNI_SERVICE_ACCOUNT_USERNAME')
password = os.getenv('DAFNI_SERVICE_ACCOUNT_PASSWORD')


def get_token():
    login_resp = requests.post(
        "https://keycloak.secure.dafni.rl.ac.uk/auth/realms/Production/protocol/openid-connect/token",
        {
            "username": username,
            "password": password,
            "client_id": "dafni-main",
            "grant_type": "password",
            "scope": "openid",
        },
    )
    login_resp.raise_for_status()
    return login_resp.json()["access_token"]


def get_headers():
    return {'Authorization': f'Bearer {get_token()}'}
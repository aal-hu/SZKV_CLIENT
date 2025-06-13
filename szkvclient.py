import requests
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://192.168.0.14:5000" 
CERT_VERIFY = False  # Set to True if you have a valid SSL certificate



if __name__ == "__main__":
    response = requests.get(
        f"{BASE_URL}/stats",
        json={"pin": 1111},
        verify=CERT_VERIFY
    )
    print("A válasz: ", response.json())



import requests
import urllib3

urllib3.disable_warnings()

BASE_URL = "https://localhost:5000" 
CERT_VERIFY = False  # Set to True if you have a valid SSL certificate



__if __name__ == "__main__":
    # This block will only run if the script is executed directly, not when imported
    response = requests.get(
        f"{BASE_URL}/stats",
        json={"pin": 1111},
        verify=CERT_VERIFY
    )
    print("A válasz: ", response.json())
    # This block will only run if the script is executed directly, not when imported


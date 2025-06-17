import os
from kivymd.app import MDApp as App
from kivymd.uix.screen import MDScreen
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.utils import platform
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer, 
) 
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldHintText,
    MDTextFieldMaxLengthText,
    MDTextFieldTrailingIcon,
    MDTextFieldHelperText)
from kivy.metrics import dp
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from functools import wraps
import urllib3

urllib3.disable_warnings()


def safe_request(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            if response:
                response.raise_for_status()  # Raise an error for bad responses
                return response
        except (RequestException, Timeout, ConnectionError, HTTPError) as e:
            print(f"Nem sikerült adatot lekérni: {e}")
            return None
    return wrapper

@safe_request
def get_data(url, params=None):
    response = requests.get(url, params=params, verify=CERT_VERIFY, timeout=10)
    return response if response.status_code == 200 else None

@safe_request
def post_data(url, data=None, json=None):
    response = requests.post(url, data=data, json=json, verify=CERT_VERIFY, timeout=10)
    return response if response.status_code == 200 else None


BASE_URL = "https://192.168.0.14:5000"
CERT_VERIFY = False  # Set to True if you have a valid SSL certificate


if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])


class PinputScreen(MDScreen):
    pass

class AppScreen(MDScreen):
    
    labeltxt = StringProperty()    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pin_path = self.get_pin_path()
        self.pin = 0
        self.load_pin()
        self.update_label("SZKV kávégép app") 
        self.get_consumer_data()

    def get_pin_path(self):
        # Mentési hely platformfüggően
        if platform == "android":
            return os.path.join(App.get_running_app().user_data_dir, "pin.txt")
        else:
            return os.path.join("data", "pin.txt")
   
    def load_pin(self):
        try:
            with open(self.pin_path, 'r') as file:
                self.pin = int(file.read())
        except (FileNotFoundError, ValueError):
            self.pin = 0

    def update_label(self, text=None):
        if text:
            self.labeltxt = text
        

    def send_coffee_request(self):
        response = post_data(f"{BASE_URL}/coffee_request", json={"pin": self.pin})"})
        if response:
            if response.status_code == 200:
                #self.update_label("Kávé kérés elküldve!")
            else:
                self.update_label(f"Hiba történt: {response.status_code} - {response.text}")
        else:
            self.update_label("Hiba történt a kávé kérés elküldésekor!")

       

    def confirm_coffee_request(self):
        response = post_data(f"{BASE_URL}/confirm_coffee_request", json={"pin": self.pin})"})
        if response:
            if response.status_code == 200:
                #self.update_label("Kávé kérés elküldve!")
            else:
                self.update_label(f"Hiba történt: {response.status_code} - {response.text}")
        else:
            self.update_label("Hiba történt a kávé kérés elküldésekor!")

        self.update_label(self.get_consumer_data())
       
    def list_consumptions(self):
        pass

    def get_consumer_data(self ):
        response = get_data(f"{BASE_URL}/consumer_data", params={"pin": self.pin})
        if response:
            if response.status_code == 200:
                self.update_label("Bejelentkezett: " + response.json('name') + "\n" +
                                  "Fogyasztások: " + str(response.json().get('consumptions'))+ "\n" +
                                  "Fizetendő fogyasztások: " + str(response.json().get('cons_payable')) + " \n" +
                                  "Fizetendő összeg: " + str(response.json().get('payable')))
            else:
                self.update_label(f"Hiba történt: {response.status_code} - {response.text}") 
        else:
            self.update_label("Hiba történt az adat lekérésnél!")

class ListScreen(MDScreen):
    pass


class SzkvApp(App):
    def __init__(self, **kwargs):
        super(SzkvApp, self).__init__(**kwargs)

    def build(self):
        self.theme_cls.primary_palette = "Brown"
        self.theme_cls.primary_hue = "500"
        #self.theme_cls.theme_style = "Light"
        return AppScreen()
   
    def on_start(self):
        # Ellenőrizzük, hogy a pin.txt létezik-e, ha nem, akkor létrehozzuk
        pin_path = AppScreen().get_pin_path()
        if not os.path.exists(pin_path):
            os.makedirs(os.path.dirname(pin_path), exist_ok=True)
            with open(pin_path, 'w') as file:
                file.write('0')
        AppScreen().load_pin()        
        if AppScreen().pin == 0:
            self.root.current = 'pinput'
            self.show_pinput_dialog()
        else:
            self.root.current = 'app_screen'

    def show_pinput_dialog(self):
        self.pinput_field = MDTextField(
            MDTextFieldHintText(
                text="Add meg a PIN kódot (4 számjegy):"
            ),
            MDTextFieldMaxLengthText(
                max_text_length=4
            ),
            mode="filled",
            size_hint=(0.8, None),
            height=50,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        dialog = MDDialog(
            MDDialogHeadlineText(
                text="PIN kód megadása"
            ),
            MDDialogContentContainer(
                self.pinput_field
            ),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Mégse"),
                    style="elevated",
                    on_release=lambda x: dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text="OK"),
                    style="elevated",
                    on_release=lambda x: self.set_pin(dialog)
                ),
                spacing=dp(30)
            ),
            size_hint=(0.8, None),
            height=200,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        dialog.open()

    def set_pin(self, dialog):
        pin = self.pinput_field.text
        if len(pin) == 4 and pin.isdigit():
            with open(AppScreen().get_pin_path(), 'w') as file:
                file.write(pin)
            dialog.dismiss()
            self.root.current = 'app_screen'
        else:
            self.pinput_field.error = True 

  
if __name__ == '__main__':
    SzkvApp().run()
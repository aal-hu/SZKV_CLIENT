import os
from kivymd.app import MDApp as App
from kivy.uix.screenmanager import ScreenManager, Screen
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
from kivymd.uix.divider import MDDivider
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldHintText,
    MDTextFieldMaxLengthText,
    MDTextFieldTrailingIcon,
    MDTextFieldHelperText)
from kivymd.uix.list import *
from kivymd.uix.snackbar import MDSnackbar, MDSnackbarSupportingText
from kivy.metrics import dp
import requests
from requests.exceptions import RequestException, Timeout, ConnectionError, HTTPError
from functools import wraps
import urllib3

urllib3.disable_warnings()

# Define a decorator to handle exceptions and log errors
def safe_request(func):
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            response = func(*args, **kwargs)
            #response.raise_for_status()  # Raise an error for bad responses
            return response
        except HTTPError as e:    
            return e.response
        except (RequestException, Timeout, ConnectionError) as e:
            print(f"Request failed: {e}")
            return None  # Return None for any request-related errors
        
    return wrapper


@safe_request
def get_data(url, params=None):
    response = requests.get(url, params=params, verify=CERT_VERIFY, timeout=10)
    return response

@safe_request
def post_data(url, data=None, json=None):
    response = requests.post(url, data=data, json=json, verify=CERT_VERIFY, timeout=10)
    return response


#BASE_URL = "https://192.168.0.14:5000"
BASE_URL = "https://bluefre.ignorelist.com:48000"
CERT_VERIFY = False  # Set to True if you have a valid SSL certificate


if platform == "android":
    from android.permissions import request_permissions, Permission
    request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

def check_pin(self, pin):
       # Ellenőrizzük, hogy a PIN kód helyes-e
    response = get_data(f"{BASE_URL}/consumer_data", params={"pin": pin})
    if response is not None:
        if response.status_code == 200:
            return True
        else:
            MDSnackbar(
                MDSnackbarSupportingText(text="Hibás vagy inaktív PIN kód!"),
                    y=dp(110),
                    pos_hint={"center_x": .5},
                    size_hint_x=0.5,
                    background_color=self.theme_cls.onPrimaryContainerColor,
            ).open()
            return False
    else:
        MDSnackbar(
            MDSnackbarSupportingText(text="Nincs szerverkapcsolat!"),
                y=dp(110),
                pos_hint={"center_x": .5},
                size_hint_x=0.5,
                background_color=self.theme_cls.onPrimaryContainerColor,
        ).open()
        return False    



class PinputScreen(MDScreen):
    pass

class AppScreen(MDScreen):
    
    labeltxt = StringProperty()    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pin_path = self.get_pin_path()
        self.pin = 0
        self.load_pin()
        if self.pin == 0:
            # Sikeres PIN megadás után még a self.pin értéke 0 úgyhogy ez lesz a kezdőképernyő
            self.update_label("A PIN kód rendben, \n az alkalmazás újraindítás után \n lesz használható. \n \n Használata: \n Jobb gomb: Kávé igénylés \n Középső gomb: Kávé igény jóváhagyása \n Bal gomb: Fogyasztás lista \n ") 
        else:    
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
        if check_pin(self, self.pin) is False:
            return
        response = post_data(f"{BASE_URL}/request_coffee", json={"pin": self.pin})
        if response is not None:
            if response.status_code == 200:
                MDSnackbar(
                    MDSnackbarSupportingText(text="Kávé igény elküldve. \n A jóváhagyáshoz nyomd meg a középső gombot \n 10mp-en belül, különben az igény törlődik. "),
                        y=dp(110),
                        pos_hint={"center_x": .5},
                        size_hint_x=0.5,
                        background_color=self.theme_cls.onPrimaryContainerColor,
                ).open()
            elif response.status_code == 400:
                MDSnackbar(                
                    MDSnackbarSupportingText(text=response.json().get('error')),
                        y=dp(110),
                        pos_hint={"center_x": .5},
                        size_hint_x=0.5,
                        background_color=self.theme_cls.onPrimaryContainerColor,
                ).open()
        else:
            self.update_label("Nincs szerverkapcsolat!")

    def confirm_coffee_request(self):
        response = post_data(f"{BASE_URL}/confirm_coffee_request", json={"pin": self.pin})
        if response is not None:
            if response.status_code == 200:
                MDSnackbar(
                    MDSnackbarSupportingText(text="Kávé fogyasztás rögzítve. \n Egészségedre!"),
                        y=dp(110),
                        pos_hint={"center_x": .5},
                        size_hint_x=0.5,
                        background_color=self.theme_cls.onPrimaryContainerColor,
                ).open()
            elif response.status_code == 400:
                MDSnackbar(                
                    MDSnackbarSupportingText(text=response.json().get('error')),
                        y=dp(110),
                        pos_hint={"center_x": .5},
                        size_hint_x=0.5,
                        background_color=self.theme_cls.onPrimaryContainerColor,
                ).open()
        # update user data        
        self.update_label(self.get_consumer_data())
        # Refresh the consumption list        
        ListScreen().list_consumptions()

       

    def get_consumer_data(self ):
        response = get_data(f"{BASE_URL}/consumer_data", params={"pin": self.pin})
        print(response)
        if response is not None:
            if response.status_code == 200:
                self.update_label("[b]Üdv a kávézóban " + response.json().get('name').split()[-1] + "![/b]\n\n" +
                                  "Össz. fogyasztásod: " + str(response.json().get('consumptions'))+ "\n\n" +
                                  "Fizetendő fogyasztásod: " + str(response.json().get('cons_payable')) + " \n\n" +
                                  "Fizetendő összeg: [b][color=ff0000]" + str(response.json().get('payable')) + "[/b][/color] Ft\n")
            else:
                self.update_label(f"Hiba történt: {response.status_code} - {response.text}") 
        else:
            self.update_label("Hiba történt az adat lekérésnél!")


class ListScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def list_consumptions(self):
        list_data = get_data(f"{BASE_URL}/consumption_data",)
        if list_data is not None:
            if list_data.status_code == 200:
                json_data = list_data.json()
                cups = json_data['data']
                for cup in cups:
                    item = MDListItem( MDListItemHeadlineText(text=cup['name']),
                            MDListItemSupportingText(text=cup['bag_id']+' - '+cup['brand']+' - '+cup['date']+' - '+cup['time']),
                            pos_hint={"center_x": .5, "center_y": .5},
                            size_hint_x=.8)
                    self.ids.list_cons.add_widget(item)    
                    self.ids.list_cons.add_widget(MDDivider())    
            else:
                self.update_label(f"Hiba történt: {list_data.status_code} - {list_data.text}")


class SzkvApp(App):
    def __init__(self, **kwargs):
        super(SzkvApp, self).__init__(**kwargs)

    def build(self):
        self.theme_cls.primary_palette = "Brown"
        self.theme_cls.primary_hue = "500"
        return Builder.load_file('szkv.kv')        
   
    def on_start(self):
        # Ellenőrizzük, hogy a pin.txt létezik-e, ha nem, akkor létrehozzuk
        pin_path = AppScreen().get_pin_path()
        if not os.path.exists(pin_path):
            os.makedirs(os.path.dirname(pin_path), exist_ok=True)
            with open(pin_path, 'w') as file:
                file.write('0')
        AppScreen().load_pin()        
        if AppScreen().pin == 0:
            #self.root.current = 'pinput'
            self.show_pinput_dialog()
        else:
            self.root.current = 'app_screen'

    def show_pinput_dialog(self):
        self.pinput_field = MDTextField(
            MDTextFieldMaxLengthText(
                max_text_length=4
            ),
            mode="outlined",
            size_hint_y=None,
            height=dp(90),
            font_style="Headline",
            role="medium",
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
                    on_release=lambda x: self.exit_app(dialog)
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
            auto_dismiss=False,
            radius=[dp(20), dp(20), dp(20), dp(20)],
        )
        dialog.open()

    def set_pin(self, dialog):
        pin = self.pinput_field.text
        if len(pin) == 4 and pin.isdigit() and check_pin(self, pin):
            with open(AppScreen().get_pin_path(), 'w') as file:
                file.write(pin)
            dialog.dismiss()
            self.root.current = 'app_screen'
        else:
            self.pinput_field.error = True 


    def exit_app(self, dialog):  
        dialog.dismiss()
        self.get_running_app().stop()


  
if __name__ == '__main__':
    SzkvApp().run()
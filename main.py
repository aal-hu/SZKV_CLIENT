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
        self.update_label()
              
        
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
            self.save_pin()
        #self.update_label()

    def update_label(self):
        self.labeltxt = 'Felhasználható belépő: '

    def send_coffee_request(self):
        self.update_label()
       

    def confirm_coffee_request(self):
        self.update_label()
       
    def list_consumptions(self):
        pass

    def save_pin(self):
        print(self.pin)
        with open(self.pin_path, 'w') as file:
            file.write(str(self.pin))
  

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
            AppScreen().pin = int(pin)
            AppScreen().save_pin()
            dialog.dismiss()
            self.root.current = 'app_screen'
        else:
            self.pinput_field.error = True 


  
if __name__ == '__main__':
    SzkvApp().run()
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.dialog import MDDialog
from kivymd.uix.spinner import MDSpinner
from kivy.clock import Clock

import cv2
from pyzbar import pyzbar
import webbrowser

Window.size = (360, 640)

KV = '''
MDScreen:
    md_bg_color: app.theme_cls.bg_normal

    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(20)
        padding: dp(20)

        MDLabel:
            text: "📡 WiFi Share Browser"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: app.theme_cls.primary_color

        MDLabel:
            text: "Scan a QR to connect to your PC's WiFi file share server."
            halign: "center"
            theme_text_color: "Secondary"

        MDRaisedButton:
            text: "📷 Scan QR Code"
            pos_hint: {"center_x": 0.5}
            on_release: app.scan_qr()

        MDSpinner:
            id: spinner
            size_hint: None, None
            size: dp(46), dp(46)
            pos_hint: {"center_x": 0.5}
            active: False

        MDRaisedButton:
            text: "🔄 Rescan"
            pos_hint: {"center_x": 0.5}
            on_release: app.scan_qr()
'''

class WiFiShareApp(MDApp):
    def build(self):
        self.theme_cls.primary_palette = "Red"
        self.theme_cls.theme_style = "Dark"
        return Builder.load_string(KV)

    def scan_qr(self):
        self.root.ids.spinner.active = True
        Clock.schedule_once(lambda dt: self._scan_qr())

    def _scan_qr(self):
        cap = cv2.VideoCapture(0)
        detected_url = None

        while True:
            ret, frame = cap.read()
            decoded_objs = pyzbar.decode(frame)
            for obj in decoded_objs:
                detected_url = obj.data.decode("utf-8")
                cv2.putText(frame, "Detected!", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.rectangle(frame, (obj.rect.left, obj.rect.top),
                              (obj.rect.left + obj.rect.width, obj.rect.top + obj.rect.height),
                              (0, 255, 0), 2)
                break

            cv2.imshow("Scan QR Code - Press Q to exit", frame)
            if detected_url or cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        self.root.ids.spinner.active = False

        if detected_url:
            self.show_dialog("✅ QR Detected", "Opening in your browser...")
            webbrowser.open(detected_url)
        else:
            self.show_dialog("❌ No QR Detected", "Please try again.")

    def show_dialog(self, title, text):
        if hasattr(self, 'dialog') and self.dialog:
            self.dialog.dismiss()

        self.dialog = MDDialog(title=title, text=text, size_hint=(0.8, None), height="200dp")
        self.dialog.open()

if __name__ == "__main__":
    WiFiShareApp().run()


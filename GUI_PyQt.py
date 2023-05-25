import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtGui import QColor, QPalette, QFont, QPainter, QPixmap
from PyQt5.QtCore import Qt
import paho.mqtt.client as mqtt
import pygame
from pygame import mixer

class PushButton(QPushButton):
    def __init__(self, text, parent):
        super().__init__(text, parent)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Set the font color and style
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        painter.setFont(font)
        painter.setPen(Qt.white)

        # Set the button color
        if self.text() == "Start":
            painter.setBrush(Qt.green)  # Start button color
        elif self.text() == "Abort":
            painter.setBrush(Qt.red)  # Abort button color
        painter.drawRoundedRect(self.rect(), 10, 10)

        # Adjust the text position
        text_rect = self.rect()
        text_rect.adjust(5, 5, -5, -5)
        painter.drawText(text_rect, Qt.AlignCenter, self.text())

class MainWindow(QMainWindow):

    pygame.init()
    mixer.init()
    mixer.music.load(r"C:\Users\Joe\Downloads\NewMusic\MusicNew.mp3")
    mixer.music.play()

    def __init__(self):
        super().__init__()

    # Add a QLabel for the image
        image_label = QLabel(self)
        image_label.setGeometry(510, 160, 200, 200)
        image_label.setPixmap(QPixmap("C:/Users/Joe/Downloads/Picc.jpg"))  # Replace with the path to your image
        image_label.setStyleSheet("border-radius: 1000px;")  # Apply border-radius to make the edges round

        self.setWindowTitle("NEXUS_MED")
        self.setGeometry(560, 240, 800, 600)

        # Create labels for the LEDs and their topics
        self.labels = []
        for i in range(4):
            led_label = QLabel(self)
            led_label.setText("ROOM NUMBER {}".format(i+1))
            led_label.setAlignment(Qt.AlignCenter)
            led = QLabel(self)
            led.setAlignment(Qt.AlignCenter)
            self.labels.append((led_label, led))

        # Set initial LED colors to gray
        for _, led in self.labels:
            self.set_led_color(led, Qt.gray)

        # Set positions of labels and LEDs manually
        self.labels[0][0].move(50, 50 + 40)
        self.labels[0][1].move(70, 80 + 40)
        self.labels[1][0].move(50, 150 + 40)
        self.labels[1][1].move(70, 180 + 40)
        self.labels[2][0].move(200, 50 + 40)
        self.labels[2][1].move(220, 80 + 40)
        self.labels[3][0].move(200, 150 + 40)
        self.labels[3][1].move(220, 180 + 40)

        # Add a bold text box in the middle of the window
        bold_label = QLabel(self)
        bold_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)  # Set the font size to 12
        bold_label.setFont(font)
        bold_label.setStyleSheet("QLabel { background-color: blue; color: white; border-radius: 10px; }")
        bold_label.setGeometry(250, 16, 330, 68)
        
        # Add a text box at the bottom of the window
        text_box = QLabel(self)
        text_box.setAlignment(Qt.AlignCenter)
        text_box.setGeometry(250, 545, 330, 42)
        text_box.setStyleSheet("QLabel { background-color: darkred; color: white; border-radius: 21px; font-weight: bold; font-size: 16px; }")
        text_box.setText("Creativity locked. All rights loaded!©")

        # Create a multi-line string for the two sentences
        text = "<span style='font-size: 23px;'>NEXUS_MED</span><br><span style='font-family: Roboto; font-size: 19px;'>Unleash the Future of Healing!</span>"
      
        # Set the multi-line text in the bold label
        bold_label.setText(text)

        # Add a text box labeled "Scissor State"
        scissor_label = QLabel(self)
        scissor_label.setAlignment(Qt.AlignCenter)
        scissor_label.setText("Scissor's State")
        scissor_label.setStyleSheet("QLabel { font-weight: bold; font-size: 16px; }")
        scissor_label.setGeometry(100, 320, 120, 30)

        # Add two LEDs labeled "UP" and "DOWN"
        up_led_label = QLabel(self)
        up_led_label.setAlignment(Qt.AlignCenter)
        up_led_label.setText("UP")
        up_led_label.setStyleSheet("QLabel { font-weight: bold; font-size: 16px; }")
        up_led_label.setGeometry(70, 360, 50, 30)

        down_led_label = QLabel(self)
        down_led_label.setAlignment(Qt.AlignCenter)
        down_led_label.setText("DOWN")
        down_led_label.setStyleSheet("QLabel { font-weight: bold; font-size: 16px; }")
        down_led_label.setGeometry(200, 360, 50, 30)

        # Create gray LEDs for UP and DOWN
        self.up_led = QLabel(self)
        self.up_led.setAlignment(Qt.AlignCenter)
        self.up_led.setGeometry(70, 390, 50, 30)
        self.set_led_color(self.up_led, Qt.gray)

        self.down_led = QLabel(self)
        self.down_led.setAlignment(Qt.AlignCenter)
        self.down_led.setGeometry(200, 390, 50, 30)
        self.set_led_color(self.down_led, Qt.gray)

        # Add a label for the scissor state
        self.scissor_state_label = QLabel(self)
        self.scissor_state_label.setAlignment(Qt.AlignCenter)
        self.scissor_state_label.setGeometry(100, 350, 120, 30)
        self.set_scissor_state("Loading")

        # Add a "Start" button
        start_button = PushButton("Start", self)
        start_button.setGeometry(280, 480, 100, 40)
        start_button.clicked.connect(self.on_start_button_clicked)

        # Add an "Abort" button
        abort_button = PushButton("Abort", self)
        abort_button.setGeometry(440, 480, 100, 40)
        abort_button.clicked.connect(self.on_abort_button_clicked)

        # Connect to the MQTT broker
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect("broker.emqx.io", 1883, 60)

        # Start the MQTT loop in a separate thread
        self.client.loop_start()

        # Track the currently active LED
        self.active_led = None

    def on_start_button_clicked(self):
        self.publish_message("inTopic", "Go")
    def on_abort_button_clicked(self):
        self.publish_message("inTopic", "Stop")
    def publish_message(self, topic, message):
        self.client.publish(topic, message)

    def on_connect(self, client, userdata, flags, rc):
        print("Connected to MQTT broker with result code " + str(rc))
        # Subscribe to topics
        self.client.subscribe("inTopic")

    def on_message(self, client, userdata, msg):
        message = msg.payload.decode()
        print("Received message on topic " + msg.topic + ": " + message)
        # Update the corresponding LED based on the received message
        if msg.topic == "inTopic":
            # Turn off the previously active LED
            if self.active_led is not None:
                self.set_led_color(self.active_led, Qt.gray)
            
            # Toggle the selected LED
            if message == "1":
                self.set_led_color(self.labels[0][1], QColor(message))
                self.active_led = self.labels[0][1]
            elif message == "2":
                self.set_led_color(self.labels[1][1], QColor(message))
                self.active_led = self.labels[1][1]
            elif message == "3":
                self.set_led_color(self.labels[2][1], QColor(message))
                self.active_led = self.labels[2][1]
            elif message == "4":
                self.set_led_color(self.labels[3][1], QColor(message))
                self.active_led = self.labels[3][1]
            elif message == "U":
                self.set_led_color(self.up_led, QColor(message))
                self.set_led_color(self.down_led, Qt.gray)
                self.active_led = self.up_led
            elif message == "D":
                self.set_led_color(self.down_led, QColor(message))
                self.set_led_color(self.up_led, Qt.gray)
                self.active_led = self.down_led

        # Update the scissor state based on the received message
        if msg.topic == "inTopic":
            if message == "SU":
                self.set_scissor_state("UP")
            elif message == "SD":
                self.set_scissor_state("DOWN")

    def set_led_color(self, led, color):
        palette = led.palette()
        if color == Qt.gray:
            # Set the LED color to gray for the inactive state
            palette.setColor(QPalette.Window, color)
        else:
            # Set a different color (e.g., red) for the active state
            active_color = QColor(255, 0, 0)  # Red color
            palette.setColor(QPalette.Window, active_color)
        led.setPalette(palette)
        led.setAutoFillBackground(True)
        led.setFixedSize(50, 50)

    def set_scissor_state(self, state):
        self.scissor_state_label.setText(state)

    def closeEvent(self, event):
        # Disconnect from the MQTT broker and stop the loop
        self.client.loop_stop()
        self.client.disconnect()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

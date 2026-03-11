from gpiozero import LED
from time import sleep

from gui.gui import MainWindow

class ControlSystem:

    def __init__ (self):

        self.led_dict = {
            "ALARM" : LED(25),      # GPIO25 (pin 22)
            "DECK" : LED(12),       # GPIO12 (pin 32)
            "TRI" : LED(16),        # GPIO16 (pin 36)
            "STEAMING" : LED(20),   # GPIO20 (pin 38)
            "ANCHOR" : LED(21),     # GPIO21 (pin 40)
            "STERN" : LED(26)       # GPIO26 (pin 37)
        }

        self.light_modes ["daytime", "anchored", "working anchored", "under sail", "under motor"]

        self.current_mode = 0


    def SetMode(self, mode):
        print(mode)

    



    def LEDOn(self, name):
        self.led_dict[name].on()

    def LEDOff(self, name):
        self.led_dict[name].off()
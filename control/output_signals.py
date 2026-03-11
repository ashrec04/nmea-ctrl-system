from gpiozero import LED
from time import sleep


led_dict = {
    "ALARM" : LED(25),      # GPIO25 (pin 22)
    "DECK" : LED(12),       # GPIO12 (pin 32)
    "TRI" : LED(16),        # GPIO16 (pin 36)
    "STEAMING" : LED(20),   # GPIO20 (pin 38)
    "ANCHOR" : LED(21),     # GPIO21 (pin 40)
    "STERN" : LED(26)       # GPIO26 (pin 37)
}

def LEDOn(name):
    led_dict[name].on()

def LEDOff(name):
    led_dict[name].off()



if __name__ == "__main__":
    while True:
        for key, value in led_dict.items():
            sleep(0.01)
            LEDOn(key)

        for key, value in led_dict.items():
            sleep(0.01)
            LEDOff(key)

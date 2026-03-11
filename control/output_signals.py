from gpiozero import LED


class ControlSystem:

    #~ globals
    MOVING_SPEED_THRESHOLD = 1.0
    STATIONARY_SPEED_THRESHOLD = 0.3
    REQUIRED_CONSECUTIVE_SAMPLES = 5
    #~

    def __init__(self):
        self.led_dict = {
            "ALARM" : LED(25),      # GPIO25 (pin 22)
            "DECK" : LED(12),       # GPIO12 (pin 32)
            "TRI" : LED(16),        # GPIO16 (pin 36)
            "STEAMING" : LED(20),   # GPIO20 (pin 38)
            "ANCHOR" : LED(21),     # GPIO21 (pin 40)
            "STERN" : LED(26),      # GPIO26 (pin 37)
        }

        self.light_modes = {
            "day_anchored": tuple(),
            "day_moving": tuple(),
            "night_anchored": ("ANCHOR",),
            "night_moving": ("TRI", "STEAMING", "STERN"),
        }

        self.daytime = True
        self.is_moving = False
        self.current_mode = None
        self._moving_samples = 0
        self._stationary_samples = 0

        self.ApplyMode()


    def UpdateDaytime(self, daytime: bool) -> None:
        if self.daytime == daytime:
            return

        self.daytime = daytime
        self.ApplyMode()


    def UpdateSpeed(self, speed_knots: float | int | None) -> None:

        if speed_knots is None:
            return

        speed = float(speed_knots)

        if speed >= self.MOVING_SPEED_THRESHOLD:
            self._moving_samples += 1
            self._stationary_samples = 0

        elif speed <= self.STATIONARY_SPEED_THRESHOLD:
            self._stationary_samples += 1
            self._moving_samples = 0

        else:
            self._moving_samples = 0
            self._stationary_samples = 0


        if self._moving_samples >= self.REQUIRED_CONSECUTIVE_SAMPLES and not self.is_moving:
            self.is_moving = True
            self.ApplyMode()

        elif self._stationary_samples >= self.REQUIRED_CONSECUTIVE_SAMPLES and self.is_moving:
            self.is_moving = False
            self.ApplyMode()


    def ApplyMode(self) -> None:
        # only sets lights if time is set to night
        if self.daytime:
            mode = "day_moving" if self.is_moving else "day_anchored"
        else:
            mode = "night_moving" if self.is_moving else "night_anchored"

        if mode == self.current_mode:
            return

        self.current_mode = mode
        enabled_leds = set(self.light_modes[mode])
        print(f"enabling {mode} mode")

        for led_name, led in self.led_dict.items():
            if led_name in enabled_leds:
                led.on()
            else:
                led.off()


    def SetMode(self, mode: str) -> None:
        if mode not in self.light_modes:
            raise ValueError(f"Unknown light mode: {mode}")

        self.current_mode = None
        enabled_leds = set(self.light_modes[mode])

        for led_name, led in self.led_dict.items():
            if led_name in enabled_leds:
                led.on()
            else:
                led.off()

    #~ Debugging commands
    def AllOn(self):
        for led_name, led in self.led_dict.items():
                led.on()

    def AllOff(self):
        for led_name, led in self.led_dict.items():
                led.off()

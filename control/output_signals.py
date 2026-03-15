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
            "night_moving_sail": ("TRI", "STEAMING", "STERN"),
            "night_moving_engine": ("TRI", "DECK", "STERN"),
        }

        self.daytime = True
        self.is_moving = False
        self.engine_running = False
        self.current_mode = None
        self._moving_samples = 0
        self._stationary_samples = 0

        self.alarm_configs = {}
        self.acknowledged_alarms = {}
        self.current_bilge_level = None
        self.alarm_state_changed_callback = None

        self.ApplyMode()


    def UpdateDaytime(self, daytime: bool) -> None:
        if self.daytime == daytime:
            return

        self.daytime = daytime
        self.ApplyMode()


    def UpdateSpeed(self, speed_knots: float | int | None) -> None: # checks current vessel speed
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


    def UpdateEngineRPM(self, rpm: float | int | None) -> None: # checks current engine rpm
        if rpm is None:
            return

        engine_running = float(rpm) > 0

        if self.engine_running == engine_running:
            return

        self.engine_running = engine_running
        self.ApplyMode()


    def ApplyMode(self) -> None:
        # only sets lights if time is set to night
        if self.daytime:
            mode = "day_moving" if self.is_moving else "day_anchored"
        elif not self.is_moving:
            mode = "night_anchored"
        elif self.engine_running:
            mode = "night_moving_engine"
        else:
            mode = "night_moving_sail"

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

    def UpdateAlarmConfig(self, pgn: str | int, config: dict) -> None:
                # fetch's alarm config after save button is pressed in gui
        pgn_key = str(pgn)
        self.alarm_configs[pgn_key] = config
        self.acknowledged_alarms[pgn_key] = False
        print(f"Config Updated {self.alarm_configs}")
        self.CheckAlarm(pgn)

    def GetAlarmConfig(self, pgn: str | int) -> dict | None:
        return self.alarm_configs.get(str(pgn))
        print(f"Config Got {self.alarm_configs}")

    def UpdateBilgeLevel(self, level: float | int | None) -> None:
        #get current bilge lvl read
        if level is None:
            return

        self.current_bilge_level = float(level)
        self.CheckAlarm("127505")

    def AcknowledgeAlarm(self, pgn: str | int = "127505") -> None:
        # turns off alarm when ack button pressed
        pgn_key = str(pgn)

        if self.CheckAlarm(pgn):
            self.acknowledged_alarms[pgn_key] = True
            self.led_dict["ALARM"].off()
            if self.alarm_state_changed_callback is not None:
                self.alarm_state_changed_callback(pgn_key, False)

    def CheckAlarm(self, pgn: str | int = "127505") -> bool:
        #check status of bilge alarm
        pgn_key = str(pgn)
        config = self.GetAlarmConfig(pgn)

        #if bilge lvl has gone below trigger
        if config is None or self.current_bilge_level is None:
            self.led_dict["ALARM"].off()
            if self.alarm_state_changed_callback is not None:
                self.alarm_state_changed_callback(pgn_key, False)
            return False

        alarm_type = config.get("alarm_type")
        threshold = config.get("threshold")


        if threshold is None:
            self.led_dict["ALARM"].off()
            if self.alarm_state_changed_callback is not None:
                self.alarm_state_changed_callback(pgn_key, False)
            return False

        threshold_value = float(threshold)

        # get the alarm status based on its type
        if alarm_type == "Higher":
            condition_active = self.current_bilge_level >= threshold_value
        elif alarm_type == "Lower":
            condition_active = self.current_bilge_level <= threshold_value
        else:
            self.led_dict["ALARM"].off()
            if self.alarm_state_changed_callback is not None:
                self.alarm_state_changed_callback(pgn_key, False)
            return False

        if not condition_active:
            self.acknowledged_alarms[pgn_key] = False
            alarm_active = False
        else:
            alarm_active = not self.acknowledged_alarms.get(pgn_key, False)

        if alarm_active:
            self.led_dict["ALARM"].on()
        else:
            self.led_dict["ALARM"].off()

        if self.alarm_state_changed_callback is not None:
            self.alarm_state_changed_callback(pgn_key, alarm_active)

        return alarm_active


    #~ Debugging commands
    def AllOn(self):
        for led_name, led in self.led_dict.items():
                led.on()

    def AllOff(self):
        for led_name, led in self.led_dict.items():
                led.off()         
    #~

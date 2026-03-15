from collections import Counter
import time
from nmea2000.encoder import NMEA2000Encoder, NMEA2000Message, NMEA2000Field
import re

from nmea2000.decoder import NMEA2000Decoder
from nmea2000.utils import calculate_canbus_checksum

import core.data_logger
from control.output_signals import ControlSystem



''' Holds the NEMAMessage Class
    A Sent CAN frame sends one bye per message so one message is recieved in 20 messages (including start and end bytes)

    Typical message:
    aa 55 01 02 01   01 0b   f5 09 08 00 dc 05 00 00 00 00 00   00 f7
                                       
'''

class NEMAMessage:
    DIAGNOSTIC_INTERVAL_SECONDS = 5
    TRACKED_PGNS = (128267, 129026, 130306, 127505, 127488)

    def __init__ (self, control_system=None):
        #initise encoder and decoder
        self.encoder = NMEA2000Encoder()
        self.decoder = NMEA2000Decoder()
        self.control_system = control_system or ControlSystem()

        self.data_recieved = False

        #debugging system
        self._diagnostic_started_at = time.monotonic()
        self._diagnostic_last_logged_at = self._diagnostic_started_at
        self._frames_seen = 0
        self._parse_failures = 0
        self._decode_failures = 0
        self._extract_failures = 0
        self._decoded_pgn_counts = Counter()
        self._delivered_pgn_counts = Counter()


    def ProcessCANFrame(self, window, frame) -> None:
        self._frames_seen += 1

        if getattr(window, "daytime_changed_callback", None) is None: # get if time of day has changed
            window.daytime_changed_callback = self.control_system.UpdateDaytime
            self.control_system.UpdateDaytime(window.daytime)

        # Extract all bytes from canusb log line
        all_bytes = self.ParseHexBytes(frame) 

        if not all_bytes:
            self._parse_failures += 1
            self.LogDiagnosticsIfDue()
            return None, []
        
        pkt = self.DecodeMessage(all_bytes)
        if pkt is None:
            self.LogDiagnosticsIfDue()
            return

        decoded_msg = self.decoder.decode_usb(pkt)

        if decoded_msg is None:
            self._decode_failures += 1
            self.LogDiagnosticsIfDue()
            return

        self._decoded_pgn_counts[decoded_msg.PGN] += 1

        value = self.ExtractNumericValue(decoded_msg)
        if value is None:
            self._extract_failures += 1
            self.LogDiagnosticsIfDue()
            return

        self._delivered_pgn_counts[decoded_msg.PGN] += 1
        window.DataInput(decoded_msg.PGN, value)
        self.UpdateControlState(decoded_msg)
        core.data_logger.LogData(pkt, decoded_msg.timestamp)
        self.LogDiagnosticsIfDue()
    

    def ParseHexBytes(self, frame: str):
        frame_match = re.search(r"Frame ID:\s*([0-9a-fA-F]{4})", frame)
        data_match = re.search(r"Data:\s*((?:[0-9a-fA-F]{2}\s*)+)", frame)

        if not frame_match or not data_match:
            return ""

        frame_id = frame_match.group(1).lower()
        id_bytes = [frame_id[:2], frame_id[2:]]
        data_bytes = [b.lower() for b in re.findall(r"[0-9a-fA-F]{2}", data_match.group(1))]

        all_bytes = " ".join(id_bytes + data_bytes)
        return all_bytes # returned in format: "id1 id0 d7 d6 d5 d4 d3 d2 d1 d0 id3 id2"


    def DecodeMessage(self, msg_bytes) -> bytes:
        # Decode the message

        rx = bytes.fromhex(msg_bytes)

        # Rebuild USB frame payload as d0..d7 before passing to decode_usb()

        data = rx[2:10][::-1]  # 8 data bytes

        # RX format is [id1 id0 data... id3 id2] so convert to little endian frame_id [id0 id1 id2 id3]
        frame_id = bytes([rx[1], rx[0], rx[11], rx[10]])

        pkt19 = bytes.fromhex("aa 55 01 02 01") + frame_id + bytes([len(data)]) + data + b"\x00"
        pkt = pkt19 + bytes([calculate_canbus_checksum(pkt19)])  # checksum uses bytes [2:19]


        return pkt

    def ExtractNumericValue(self, decoded_msg):
        fields_by_id = {fld.id: fld.value for fld in decoded_msg.fields}

        if decoded_msg.PGN == 127505:
            level = fields_by_id.get("level")
            capacity = fields_by_id.get("capacity")

            if isinstance(level, (int, float)) and isinstance(capacity, (int, float)):
                return (level / 100) * capacity

            if isinstance(level, (int, float)):
                return level

        if decoded_msg.PGN == 127488:
            speed = fields_by_id.get("speed")
            if isinstance(speed, (int, float)):
                return speed

        for fld in decoded_msg.fields:
            if fld.id =="depth" or fld.id =="windSpeed" or fld.id =="sog" :
                return fld.value

        return None

    def UpdateControlState(self, decoded_msg) -> None:
        for fld in decoded_msg.fields:
            if fld.id == "sog":
                self.control_system.UpdateSpeed(fld.value)
            elif decoded_msg.PGN == 127505 and fld.id == "level":
                self.control_system.UpdateBilgeLevel(fld.value)
            elif decoded_msg.PGN == 127488 and fld.id == "speed":
                self.control_system.UpdateEngineRPM(fld.value)

    def LogDiagnosticsIfDue(self) -> None:
        now = time.monotonic()
        if now - self._diagnostic_last_logged_at < self.DIAGNOSTIC_INTERVAL_SECONDS:
            return

        elapsed_seconds = max(now - self._diagnostic_started_at, 0.001)
        decoded_summary = ", ".join(
            f"{pgn}:{self._decoded_pgn_counts.get(pgn, 0)}"
            for pgn in self.TRACKED_PGNS
        )
        delivered_summary = ", ".join(
            f"{pgn}:{self._delivered_pgn_counts.get(pgn, 0)}"
            for pgn in self.TRACKED_PGNS
        )

        core.data_logger.LogProgram(
            "NMEA diagnostics "
            f"elapsed={elapsed_seconds:.1f}s "
            f"frames_seen={self._frames_seen} "
            f"parse_failures={self._parse_failures} "
            f"decode_failures={self._decode_failures} "
            f"extract_failures={self._extract_failures} "
            f"decoded_pgns=[{decoded_summary}] "
            f"delivered_pgns=[{delivered_summary}]"
        )
        self._diagnostic_last_logged_at = now
        

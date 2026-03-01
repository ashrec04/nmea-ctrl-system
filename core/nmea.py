from nmea2000.encoder import NMEA2000Encoder, NMEA2000Message, NMEA2000Field
import re

from nmea2000.decoder import NMEA2000Decoder
from nmea2000.utils import calculate_canbus_checksum


''' Holds the NEMAMessage Class
    A Sent CAN frame sends one bye per message so one message is recieved in 20 messages (including start and end bytes)

    Typical message:
    aa 55 01 02 01   01 0b   f5 09 08 00 dc 05 00 00 00 00 00   00 f7
                                       
'''

class NEMAMessage:

    def __init__ (self):
        #initise encoder and decoder
        self.encoder = NMEA2000Encoder()
        self.decoder = NMEA2000Decoder()

        self.START_FRAME = "aa"

        self.message_len_count = 0

        self.message = ""

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
    
    def ProcessCANFrame(self, frame):
        # Extract all bytes from canusb log line
        all_bytes = self.ParseHexBytes(frame) 

        if not all_bytes:
            return None, []
        
        self.DecodeMessage(all_bytes)
    

    def DecodeMessage(self, msg_bytes) -> None:
        # Decode the message

        rx = bytes.fromhex(msg_bytes)

        # Rebuild USB frame payload as d0..d7 before passing to decode_usb()

        data = rx[2:10][::-1]  # 8 data bytes

        # RX format is [id1 id0 data... id3 id2] so convert to little endian frame_id [id0 id1 id2 id3]
        frame_id = bytes([rx[1], rx[0], rx[11], rx[10]])

        pkt19 = bytes.fromhex("aa 55 01 02 01") + frame_id + bytes([len(data)]) + data + b"\x00"
        pkt = pkt19 + bytes([calculate_canbus_checksum(pkt19)])  # checksum uses bytes [2:19]


        decoded_msg = self.decoder.decode_usb(pkt)
        
        self.LogMessage(decoded_msg)

             
    def LogMessage(self, decoded_msg) -> None:
        try:
            entry = f"PGN {decoded_msg.PGN}: {[(fld.id, fld.value) for fld in decoded_msg.fields]}" # add to log
        except:
            entry = decoded_msg
        print(f"message logged <<< {entry}")
        

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

    def ParseHexBytes(text: str):
        return [b.lower() for b in re.findall(r"\b[0-9a-fA-F]{2}\b", text)]
    
    def ProcessCANFrame(self, frame):
        # Extract all bytes from canusb log line
        all_bytes = self.ParseHexBytes(frame)

        if not all_bytes:
            return None, []
        
        self.DecodeMessage(all_bytes)

        return all_bytes[0], all_bytes
    
    '''
    def ProcessFrame(self, frame) -> None:

        if frame == self.START_FRAME:
            # save completed message and reset variables to start assembling new message

            if self.message:
                self.LogMessage()

            self.message = ""
            self.message_len_count = 0

            self.message += frame
        
        else:
            self.message += frame
            self.message_len_count += 1
    '''

    def DecodeMessage(self, msg_bytes) -> None:
        # Decode the message

        rx = bytes.fromhex(msg_bytes)
        data = rx[2:10]  # 8 data bytes
        frame_id = bytes([rx[1], rx[0], rx[11], rx[10]]) # converting frame id from little endian to get [id0, id1, id2, id3]

        pkt19 = bytes.fromhex("aa 55 01 02 01") + frame_id + bytes([len(data)]) + data # add common first 5 bytes
        pkt = pkt19 + bytes([calculate_canbus_checksum(pkt19 + b"\x00")])  # checksum uses bytes[2:19]
        
        decoder = NMEA2000Decoder()
        msg = decoder.decode_usb(pkt)
        print(msg.to_json() if msg else "no decode")
        
        # self.LogMessage()

             
    def LogMessage(self) -> None:
        print("message logged <<< ", self.message)
        


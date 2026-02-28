from nmea2000.encoder import NMEA2000Encoder, NMEA2000Message, NMEA2000Field
from nmea2000.decoder import NMEA2000Decoder

''' Holds the NEMAMessage Class
    A Sent CAN frame sends one bye per message so one message is recieved in 20 messages (including start and end bytes)

    Typical message:
    aa 55   01 02 01 01 02 f8 09 08 00 00 00 00 00 00 00 00 00 10
    |---|     
   Start              
   bytes                                        
'''

class NEMAMessage:
    def __init__ (self):
        #initise encoder and decoder
        self.encoder = NMEA2000Encoder()
        self.decoder = NMEA2000Decoder()

        self.START_FRAME_ONE = "aa"
        self.START_FRAME_TWO = "55"

        self.start_one = False

        self.MESSAGE_LEN = 40 # message len = 20 bytes (doubled for nibbles)
        self.message_len_count = 0

        self.tmp_frame = ""
        self.message = ""

    def ProcessFrame(self, frame):

        if frame == self.START_FRAME_ONE:

            if self.message:
                print("<<< ", self.message)

            self.message = ""
            self.message_len_count = 0

            self.message += frame
        
        else:
            self.message += frame
            self.message_len_count += 1
             
    def LogMessage(self):
        print("message logged >>> ", self.message)    


    def BuildMessage(self, frame):
        print("hello :D")


    def DecodeMessage(self, msg_bytes):
        # Decode the message
        decoded = None
        for b in msg_bytes:
            d = self.decoder.decode_tcp(b)
            if d:
                decoded = d
        return decoded


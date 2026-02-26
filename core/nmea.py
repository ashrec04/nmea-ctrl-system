from nmea2000.encoder import NMEA2000Encoder, NMEA2000Message, NMEA2000Field
from nmea2000.decoder import NMEA2000Decoder

''' Holds the NEMAMessage Class
    A Sent CAN frame sends one bye per message so one message is recieved in 14 messages (including start and end bytes)

    Typical message:
    aa 55   12 07 01 00 00 00 00 00 00 00 00 00 01 00 00 00 00 1b
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

        self.MESSAGE_LEN = 14 # message len = 12 + start bytes
        self.message_len_count = 0

        self.tmp_frame = ""
        self.message = ""

    def ProcessFrame(self, frame):

        if frame == self.START_FRAME_ONE:
            print("START?")
            self.tmp_frame = frame
        
        elif frame == self.START_FRAME_TWO:
            print("START!!")

            self.message += self.tmp_frame
            self.message += frame

            self.tmp_frame = ""
        
        elif self.message_len_count <  self.MESSAGE_LEN:
            self.message += frame
            self.message_len_count += 1
        
        else: #message end
            print("<<< ", self.message)
            print("END")
            
            self.message = ""
            self.message_len_count = 0
             
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


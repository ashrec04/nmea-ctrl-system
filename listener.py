from nmea2000.decoder import NMEA2000Decoder

class NMEADecoder:
    def __init__ (self):
        #initise decoder
        self.decoder = NMEA2000Decoder()
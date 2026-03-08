import logging
from datetime import datetime, timedelta
from nmea2000.decoder import NMEA2000Decoder
from pathlib import Path
import os
import re

#~ Constants
DATA_LOG_PTH = "logs/data.log"
PROGRAM_LOG_PTH = "logs/program.log"

LOG_REDUCE_SAMPLES_THRESHOLD_DAYS = 1
LOG_DELETE_THRESHOLD_DAYS = 7

SAMPLE_RATE_REDUCE_FACTOR = 10
#~ 


def LogData(data: bytes, timestamp):
    with open(DATA_LOG_PTH, "a") as f:
        ts = timestamp.isoformat(timespec="seconds") # save timestamp in format YYYY-MM-DDTHH:MM:SS
        f.write(f"{ts} : {data.hex(" ")}\n")


def LogProgram(msg): #TODO get this to save on the log file not in console
    logger = logging.getLogger(PROGRAM_LOG_PTH)
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s" # TODO get function name to be where function is called not LogProgram
    logging.basicConfig(format=FORMAT)
    logger.setLevel(logging.DEBUG)
    logger.debug(msg)


def LogError(e):
    with open(PROGRAM_LOG_PTH, "a") as f:
        f.write("\n")
        f.write(e)


def CleanLog():
    '''
        Data is stored in full for 1 day
        Data between 1 to 7 days old has sample rate decreased by a factor of 10
        Data older than 7 days is deleted
    '''
    
    LogProgram("cleaning data log...")

    decoder = NMEA2000Decoder()
    time_now = datetime.now()

    reduce_sample_rate = time_now - timedelta(days=LOG_REDUCE_SAMPLES_THRESHOLD_DAYS)
    delete_all = time_now - timedelta(days=LOG_DELETE_THRESHOLD_DAYS)

    # reduce_sample_rate = time_now - timedelta(minutes=LOG_REDUCE_SAMPLES_THRESHOLD_DAYS)
    # delete_all = time_now - timedelta(minutes=LOG_DELETE_THRESHOLD_DAYS)

    sample_count = 0
    messages_removed = 0
    oldest_data = ""

    src = Path(DATA_LOG_PTH)
    tmp = src.with_suffix(src.suffix + ".tmp") # temp file made
    rev = src.with_suffix(src.suffix + ".rev")  # moves temp into it in reverse then to log so the order isnt flipped

    with src.open("r") as fin, tmp.open("w") as fout: # opend LOGPATH as r and temp as write
        for line in fin: # read LOGPATH line by line
            remove_line = False

            try:
                data_time_str, data = line.strip().split(" : ", 1) #splits timestamp and data
                data_time = datetime.fromisoformat(data_time_str)
                data = bytes.fromhex(data)
            except:
                continue

            if len(data) < 20: # protects against empty or incorrect lines in log
                continue

            if delete_all > data_time: # if data is older than LOG_DELETE_THRESHOLD_DAYS
                remove_line = True

            elif reduce_sample_rate > data_time: # if data is older than LOG_REDUCE_SAMPLES_THRESHOLD_DAYS
                #delete 9 in 10 messages
                if sample_count != SAMPLE_RATE_REDUCE_FACTOR:
                    remove_line = True
                    sample_count += 1
                else:
                    sample_count = 0 # reset count
                    print(f"Sample rate reduced: {data_time} difference {data_time - reduce_sample_rate}")


            if remove_line == True: # removed line isnt written to temp
                messages_removed +=1
                oldest_data = data_time
                continue

            fout.write(line)

    os.replace(tmp, src)  #  replaces LOGPATH with rev
    tmp.unlink(missing_ok=True)


    
    LogProgram(f"log cleaning successful: removed {messages_removed} lines, oldest data removed = {oldest_data}")

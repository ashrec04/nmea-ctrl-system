import logging

DATA_LOG_PTH = "logs/data.log"
PROGRAM_LOG_PTH = "logs/program.log"

def LogData(data: bytes):
    with open(DATA_LOG_PTH, "a") as f:
        f.write("\n")
        f.write(data.hex(" "))

def LogProgram(msg):
    logger = logging.getLogger(PROGRAM_LOG_PTH)
    FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
    logging.basicConfig(format=FORMAT)
    logger.setLevel(logging.DEBUG)
    logger.debug(msg)


def LogError(e):
    with open(PROGRAM_LOG_PTH, "a") as f:
        f.write("\n")
        f.write(e)

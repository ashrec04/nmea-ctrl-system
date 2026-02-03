import subprocess
import os

def main():
    #===================================#
    # Read data sent from CAN USB Port  #
    #===================================#

    project_dir = "USB-CAN-A"  # Path to waveshare USB-CAN code
    os.chdir(project_dir)   # change directory to folder
    subprocess.run(["sudo", "make", "clean"], check=True)
    subprocess.run(["sudo", "make"], check=True)

    #run the canusb program command
    # sudo ./canusb -t -d /dev/ttyUSB0 -s 125000 -t
    subprocess.run([
        "sudo", "./canusb",
        "-t",
        "-d", "/dev/ttyUSB0",   # TTY device used
        "-s", "125000",         # CAN Baud rate 125K for NMEA2000
        "-t"
    ], check=True)


if __name__ == "__main__":
    main()

import os
import sys
import time
import subprocess
from pathlib import Path

import can
from nmea2000.decoder import NMEA2000Decoder


SERIAL_BAUD = 2_000_000           #Waveshare USB-CAN-A UART default
CAN_BITRATE = 250_000             #NMEA2000 rate
DEFAULT_IFACE = "usb0"


def run(cmd: list[str]) -> None:
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"{' '.join(cmd)} failed: {res.stderr.strip() or res.stdout.strip()}")


def find_serial_dev() -> str: #locate USB-CAN device
    for dev in ["/dev/ttyUSB0", "/dev/ttyUSB1", "/dev/ttyACM0", "/dev/ttyACM1"]:
        if Path(dev).exists():
            print(f"Found USB-CAN serial device at {dev}")
            return dev
    raise FileNotFoundError("No USB-CAN serial device found (ttyUSB*/ttyUSB*).")


def ensure_can_interface(iface: str = DEFAULT_IFACE) -> None:
    #is it already up
    check = subprocess.run(["ip", "link", "show", iface], capture_output=True)
    if check.returncode == 0 and b"UP" in check.stdout:
        return

    serial = find_serial_dev()
    #load kernel modules
    for mod in ("can", "can_raw", "slcan"):
        subprocess.run(["modprobe", mod], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # kill stale slcand if any
    subprocess.run(["pkill", "slcand"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    #start slcand to map serial ---> socketcan
    run(["sudo", "slcand", "-o", "-c", f"-s5", f"-S", str(SERIAL_BAUD), serial, iface])
    print("CMD:", "sudo", "slcand", "-o", "-c", f"-s5", f"-S", str(SERIAL_BAUD), serial, iface)
    time.sleep(0.2)  #time to load
    run(["ip", "link", "set", iface, "up", "type", "can", "bitrate", str(CAN_BITRATE)])
    print("CMD:","ip", "link", "set", iface, "up", "type", "can", "bitrate", str(CAN_BITRATE))


class NMEAListener:
    def __init__(self, iface: str = DEFAULT_IFACE, decode: bool = True):
        self.iface = iface
        self.decode = decode
        self.decoder = NMEA2000Decoder() if decode else None
        ensure_can_interface(iface)
        self.bus = can.Bus(channel=iface, bustype="socketcan")

    def start(self):
        print(f"Listening on {self.iface}. Ctrl+C to stop.")
        try:
            for msg in self.bus:
                line = f"{msg.timestamp:.3f} ID {msg.arbitration_id:08X} DLC {msg.dlc} Data " \
                       f"{' '.join(f'{b:02X}' for b in msg.data)}"
                if self.decoder:
                    try:
                        decoded = self.decoder.decode(msg.arbitration_id, bytes(msg.data))
                        if decoded:
                            line += f" -> {decoded}"
                    except Exception as err:
                        line += f" (decode error: {err})"
                print(line, flush=True)
        except KeyboardInterrupt:
            print("\nStopping listener...")
        finally:
            self.bus.shutdown()


if __name__ == "__main__":
    NMEAListener().start()

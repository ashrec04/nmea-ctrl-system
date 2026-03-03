import asyncio
import contextlib
import signal
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import QApplication
import sys
from qasync import QEventLoop


from core.nmea import NEMAMessage
import core.data_logger
from gui.gui import MainWindow


PROJECT_DIR = Path(__file__).resolve().parent / "USB-CAN-A"
CANUSB_BIN = PROJECT_DIR / "canusb"
BAUD_RATE = 125000
TTY_DEV = "/dev/ttyUSB0"


def BuildCanusb() -> None:
    subprocess.run(["sudo","make", "clean"], cwd=PROJECT_DIR, check=True)
    subprocess.run(["sudo","make"], cwd=PROJECT_DIR, check=True)
    core.data_logger.LogProgram("CAN USB Communication Built")


async def DrainStderr(proc: asyncio.subprocess.Process) -> None:
    while True:
        line = await proc.stderr.readline()
        if not line:
            break
        print(f"canusb stderr: {line.decode(errors='replace').rstrip()}")


async def ListenCanFrames() -> None:
    n2k = NEMAMessage()

    # run the canusb program command
    # ~/USB-CAN-A $ ./canusb -d /dev/ttyUSB0 -s 125000
    proc = await asyncio.create_subprocess_exec(
        str(CANUSB_BIN),
        "-d", TTY_DEV,          # TTY device used
        "-s", str(BAUD_RATE),   # CAN Baud rate, 125K for NMEA2000
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=PROJECT_DIR,
    )
    assert proc.stdout is not None
    assert proc.stderr is not None
    stderr_task = asyncio.create_task(DrainStderr(proc))
    core.data_logger.LogProgram("CAN USB Communication Channel Open")


    try:
        while True:
            line = await proc.stdout.readline()

            if not line:
                break

            frame = line.decode(errors="replace").strip()
            
            if frame is not None:
                n2k.ProcessCANFrame(frame)

            else:
                print(f"canusb: {frame}")


    finally:
        if proc.returncode is None:
            proc.send_signal(signal.SIGINT)
            with contextlib.suppress(asyncio.TimeoutError):
                await asyncio.wait_for(proc.wait(), timeout=2)
            if proc.returncode is None:
                proc.kill()
                await proc.wait()

        stderr_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await stderr_task


async def main() -> None:
    app = QApplication(sys.argv)
    loop = QEventLoop(app) # initises the gui through asyncio

    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()

    with loop:
        loop.run_forever()

    core.data_logger.LogProgram("Program Start")
    BuildCanusb()
    await ListenCanFrames()


if __name__ == "__main__":
    asyncio.run(main())

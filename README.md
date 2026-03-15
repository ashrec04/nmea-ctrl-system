# NMEA2000 Control System 
Built for use on a Raspberry Pi. Receives data via a [Waveshare USB-CAN-A Bus](https://www.waveshare.com/wiki/USB-CAN-A). recieved messages are decoded and displayed on a Touchscreen interactable GUI. Data is also analysed by a control system which outputs data to GPIO Pins in relation to recieved NMEA2000 messages.

## Key Libraries Used
```
nmea2000
asyncio
subprocess
qasync
PyQt6
pyqtgraph
```

## Code Used
[Waveshare USB-CAN-A Demo](https://www.waveshare.com/wiki/USB-CAN-A) is used as a base and then modified to recieve the 20 Byte NMEA2000 Messages.


## File Structure
```  
nmea_ctrl_system
├── control
│   ├── output_signals.py
├── core
│   ├── data_logger.py
│   ├── nmea.py
├── gui
│   ├── gui.py
│   ├── widget_presets.py
│   └── resources
│       ├── alarm_widget.ui
│       ├── icon.png
│       └── mainwindow.ui
├── logs
│   ├── data.log
│   ├── data.log.log
│   └── program.log
├── main.py
├── README.md
└── USB-CAN-A
    ├── canusb
    ├── canusb.c
    ├── LICENSE
    ├── Makefile
    └── README.md
```

from nanpy import ArduinoApi
from nanpy import SerialManager

connection = SerialManager(device='/dev/tty.usbmodem1421')

a = ArduinoApi(connection=connection)

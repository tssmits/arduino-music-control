from nanpy import ArduinoApi
from nanpy import SerialManager

connection = SerialManager(device='/dev/ttyACM0')

a = ArduinoApi(connection=connection)

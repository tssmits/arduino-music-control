from nanpy import ArduinoApi
from nanpy import SerialManager

connection = SerialManager()
a = ArduinoApi(connection=connection)

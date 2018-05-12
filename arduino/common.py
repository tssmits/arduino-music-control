from nanpy import ArduinoApi
from nanpy import SerialManager

connection = SerialManager()
a = ArduinoApi(connection=connection)

# udevadm info --query=all --name=/dev/ttyACM0
# grep ID_SERIAL of /dev/serial/by-id

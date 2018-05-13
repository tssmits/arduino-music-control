class LedSingle(object):
  def __init__(self, brightness=255):
    self.brightness = brightness

  def frame(self, millis):
    return self.brightness

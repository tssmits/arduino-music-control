class LedBlinker(object):
  def __init__(self, freq, countdown=None):
    self.freq = float(freq)
    self.led_on = False
    self.millis = None
    self.countdown = countdown
    if self.countdown is not None:
      self.countdown *= 2

  def frame(self, millis):
    if self.countdown is False:
      return 0

    if self.millis is None:
      self.millis = millis

    if self.millis + (1.0 / self.freq * 1000) < millis:
      self.millis = millis
      self.led_on = not self.led_on

      if self.countdown is not None:
        self.countdown -= 1
        if self.countdown <= 0:
          self.countdown = False

    return 255 if self.led_on else 0

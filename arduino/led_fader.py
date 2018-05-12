class LedFader(object):
  def __init__(self, freq):
    self.freq = float(freq) * 2
    self.millis = None
    self.direction = 1

  def frame(self, millis):
    if self.millis is None:
      self.millis = millis

    threshold = self.millis + (1.0 / self.freq * 1000.0)

    if threshold > millis:
      diff = threshold - millis
      mx = 1.0 / self.freq * 1000.0
      if self.direction == 1:
        return int((mx - diff) / mx * 255.0)
      else:
        return int((diff) / mx * 255.0)
    else:
      self.millis = millis
      if self.direction == 1:
        self.direction = -1
        return 255
      else:
        self.direction = 1
        return 0

import os
if os.getenv("EMULATOR", "false") == "true": # change this before pushing
  from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
  from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time


import time

import time
import math

class Manager:
  def __init__(self):
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 128
    options.gpio_slowdown = 4
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = "adafruit-hat"

    self.matrix = RGBMatrix(options=options)

  def run_test(self):
    canvas = self.matrix.CreateFrameCanvas()
    t = 0

    while True:
      for x in range(self.matrix.width):
        for y in range(self.matrix.height):

          r = int((math.sin((x + t) * 0.05) + 1) * 127)
          g = int((math.sin((y + t) * 0.05) + 1) * 127)
          b = int((math.sin((x + y + t) * 0.05) + 1) * 127)

          canvas.SetPixel(x, y, r, g, b)

      canvas = self.matrix.SwapOnVSync(canvas)
      t += 1
      time.sleep(0.02)

if __name__ == "__main__":
  manager = Manager()
  manager.run_test()

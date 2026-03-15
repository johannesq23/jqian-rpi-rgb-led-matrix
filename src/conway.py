import os
if os.getenv("EMULATOR", "false") == "true": # change this before pushing
  from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
  from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time


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

  def run_game(self):
    canvas = self.matrix.CreateFrameCanvas()
    canvas.Fill(0, 0, 0)
    canvas = self.matrix.SwapOnVSync(canvas)
    time.sleep(10)


manager = Manager()

manager.run_game()


import os
if os.getenv("EMULATOR", "false") == "true": # change this before pushing
  from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
  from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import time


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

  def run_test(self):
    canvas = self.matrix.CreateFrameCanvas()
    
    # Draw a simple color gradient across the matrix
    for x in range(self.matrix.width):
      for y in range(self.matrix.height):
        r = int((x / self.matrix.width) * 255)
        g = int((y / self.matrix.height) * 255)
        b = 128
        canvas.SetPixel(x, y, r, g, b)
    
    # Swap the canvas to display
    canvas = self.matrix.SwapOnVSync(canvas)
    print("Test pattern displayed for 10 seconds...")
    time.sleep(10)

if __name__ == "__main__":
  manager = Manager()
  manager.run_test()

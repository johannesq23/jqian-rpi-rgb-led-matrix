import os
if os.getenv("EMULATOR", "false") == "true": # change this before pushing
  from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
  from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

import time
from PIL import Image, ImageDraw, ImageFont
import io

class Manager:
  def __init__(self):
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.gpio_slowdown = 4
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = "adafruit-hat"

    self.matrix = RGBMatrix(options=options)

  @property
  def width(self):
    """Get the display width."""
    if hasattr(self, 'matrix') and self.matrix is not None:
      return self.matrix.width
    elif hasattr(self, 'image'):
      return self.image.width
    else:
      return 128

  @property
  def height(self):
    """Get the display height."""
    if hasattr(self, 'matrix') and self.matrix is not None:
      return self.matrix.height
    elif hasattr(self, 'image'):
      return self.image.height
    else:
      return 32
    
  @property
  def text_offset(self):
    return 2

  def draw_subway(self):
    # image = Image.open("../assets/png/f.png").convert('RGB')

    x_pos = 16 - self.text_offset
    while True:
      x_pos -= 1
      image = Image.open("../assets/f.png").convert("RGB")
      canvas = self.matrix.CreateFrameCanvas()
      mainfont = graphics.Font()
      mainfont.LoadFont("../rpi-rgb-led-matrix-master/fonts/helvR12.bdf")

      text_color = graphics.Color(255, 255, 255)
      graphics.DrawText(canvas, mainfont, x_pos , 16 - 4, text_color, "2nd Av To Jamaica 179-St")

      for i in range(self.height // 2):
        for j in range(self.height):
          canvas.SetPixel(i, j, 0, 0, 0)

      canvas.SetImage(image, 1, 1)

      canvas = self.matrix.SwapOnVSync(canvas)

      time.sleep(0.05)


    

manager = Manager()
manager.draw_subway()
time.sleep(100)
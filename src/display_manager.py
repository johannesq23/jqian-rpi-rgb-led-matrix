from rgbmatrix import RGBMatrix, RGBMatrixOptions

from PIL import Image, ImageDraw, ImageFont

class Manager:
  def __init__(self):
    self.options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.gpio_slowdown = 4
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = "adafruit-hat"

    self.matrix = RGBMatrix(options=options)

  def draw_subway():

    

import os
if os.getenv("EMULATOR", "false") == "true": # change this before pushing
  from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
  from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

import time
from PIL import Image, ImageDraw, ImageFont
import io
from transit import Transit

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

    self.transit = Transit()

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
    return 1

  def draw_subway(self, id, duration=15):
    end_time = time.time() + duration

    x_pos = 16 - self.text_offset
    first_disp = True

    stop_info = self.transit.get_times_by_id(id)

    def extract_time(entry):
      if not isinstance(entry, dict):
        return "_min"
      return f"{entry.get('time_till_departure_mins', '_')}min"
    def extract_final_stop(entry):
      if not isinstance(entry, dict):
        return ""
      return entry.get('final_stop', "")

    # Safely pick two entries (or placeholders)
    entries = (stop_info + [{}, {}])[:2]

    first_time_mins  = extract_time(entries[0])
    second_time_mins = extract_time(entries[1])
    final_stop = extract_final_stop(entries[0])

    canvas = self.matrix.CreateFrameCanvas()
    text_font = graphics.Font()
    text_font.LoadFont("../rpi-rgb-led-matrix-master/fonts/helvR12.bdf")

    text_color = graphics.Color(255, 255, 255)
    time_color = graphics.Color(0, 200, 17)

    text_width = graphics.DrawText(canvas, text_font, 0, 0, text_color, final_stop)
    time_width = graphics.DrawText(canvas, text_font, 0, 0, time_color, first_time_mins)
    time_width += 2

    scroll = (self.width - self.height // 2 - time_width) < text_width

    image = Image.open("../assets/f.png").convert("RGB")


    while time.time() < end_time:

      graphics.DrawText(canvas, text_font, x_pos, 16 - 4, text_color, final_stop)

      x = self.width - time_width

      # Draw Black Rectangle for logo
      for i in range(self.height // 2):
        for j in range(self.height):
          canvas.SetPixel(i, j, 0, 0, 0)

      for rx in range(x, self.width):
        for ry in range(self.height):
          canvas.SetPixel(rx, ry, 0, 0, 0)

      graphics.DrawText(canvas, text_font, x, 16-4, time_color, first_time_mins)

      canvas.SetImage(image, 1, 1)

      canvas = self.matrix.SwapOnVSync(canvas)

      if first_disp:
        time.sleep(4)
        first_disp = False
      if scroll:
        x_pos -= 1
        if x_pos + text_width < 0:
          time.sleep(1)
          x_pos = 16 - self.text_offset
          first_disp = True
      time.sleep(0.05)

  def main_control_loop(self, subway_ids):
    for id in subway_ids:
      self.draw_subway(id)
      print(id)

    

manager = Manager()
while True:
  manager.main_control_loop(["F14N", "F14S"])

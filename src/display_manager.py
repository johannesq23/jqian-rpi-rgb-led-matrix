import os
if os.getenv("EMULATOR", "false") == "true": # change this before pushing
  from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
  from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

import time
from PIL import Image, ImageDraw, ImageFont
import io
from transit import Transit
import threading

class TransitCache:
  def __init__(self, transit_client, refresh_interval = 10):
    self.transit = transit_client
    self.refresh_interval = refresh_interval
    self.cache = {}
    self.lock = threading.Lock()
    self.running = True
    threading.Thread(target=self._fetch_loop, daemon=True).start()

  def _fetch_loop(self):
    while self.running:
      ids = self.cache.keys()
      for stop_id in ids:
        try:
          data = self.transit.get_times_by_id(stop_id)
          with self.lock:
            self.cache[stop_id] = data
        except Exception as e:
          print("Fetch error:", e)
      time.sleep(self.refresh_interval)
  
  def register(self, stop_id):
    with self.lock:
      if stop_id not in self.cache:
        self.cache[stop_id] = []

    try:
      data = self.transit.get_times_by_id(stop_id)
      with self.lock:
        self.cache[stop_id] = data
    except:
      pass

  def get(self, stop_id):
    with self.lock:
      return list(self.cache.get(stop_id, []))
    


class Row:
  def __init__(self, canvas, text_font, top, width, height, stop_info, logo):
    self.width = width
    self.height = height
    self.text_font = text_font
    self.y_pos = 16 if top else 32
    self.text_x_pos = 16 - self.text_offset
    self.first_disp = True
    self.first_disp_time = time.time()

    stop_info = stop_info

    entries = (stop_info + [{}, {}])[:2]
    self.first_time_mins  = self.extract_time(entries[0])
    second_time_mins = self.extract_time(entries[1])
    self.final_stop = self.extract_final_stop(entries[0])
    self.logo = logo

    self.text_width = graphics.DrawText(canvas, self.text_font, 0, 0, graphics.Color(0,0,0), self.final_stop)
    self.time_width = graphics.DrawText(canvas, self.text_font, 0, 0, graphics.Color(0,0,0), self.first_time_mins)
    self.time_width += 2
    self.scroll = (self.width - self.height // 2 - self.time_width) < self.text_width

  def draw(self, canvas):
    text_color = graphics.Color(255, 255, 255)
    time_color = graphics.Color(0, 200, 17)

    graphics.DrawText(canvas, self.text_font, self.text_x_pos, self.y_pos-4, text_color, self.final_stop)
    x = self.width - self.time_width

    # Draw Black Rectangle for logo
    for i in range(self.height // 2):
      for j in range(self.y_pos - 16, self.y_pos):
        canvas.SetPixel(i, j, 0, 0, 0)

    for rx in range(x, self.width):
      for ry in range(self.y_pos - 16, self.y_pos):
        canvas.SetPixel(rx, ry, 0, 0, 0)

    graphics.DrawText(canvas, self.text_font, x, self.y_pos-4, time_color, self.first_time_mins)

    canvas.SetImage(self.logo, 1, self.y_pos - 16 + 1)

    # canvas = self.matrix.SwapOnVSync(canvas)
    if self.first_disp:
      if time.time() - self.first_disp_time > 2:
        self.first_disp = False
    elif self.scroll:
      self.text_x_pos -= 1
      if self.text_x_pos + self.text_width < 0:
        self.text_x_pos = 16 - self.text_offset
        self.first_disp = True
        self.first_disp_time = time.time()

  @property
  def text_offset(self):
    return 1
  
  def extract_time(self, entry):
    if not isinstance(entry, dict):
      return "_min"
    return f"{entry.get('time_till_departure_mins', '_')}min"
  def extract_final_stop(self, entry):
    if not isinstance(entry, dict):
      return "_"
    return entry.get("final_stop", "_")
  def extract_route_id(self, entry):
    if not isinstance(entry, dict):
      return "_"
    return entry.get("route", "_")



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

    self.transit = Transit()
    self.text_font = graphics.Font()
    self.text_font.LoadFont("../rpi-rgb-led-matrix-master/fonts/helvR12.bdf")
    self.image_cache = {"1": Image.open("../assets/1.png").convert("RGB"),
                        "2": Image.open("../assets/2.png").convert("RGB"),
                        "3": Image.open("../assets/3.png").convert("RGB"),
                        "4": Image.open("../assets/4.png").convert("RGB"),
                        "5": Image.open("../assets/5.png").convert("RGB"),
                        "6": Image.open("../assets/6.png").convert("RGB"),
                        "a": Image.open("../assets/a.png").convert("RGB"),
                        "b": Image.open("../assets/b.png").convert("RGB"),
                        "c": Image.open("../assets/c.png").convert("RGB"),
                        "d": Image.open("../assets/d.png").convert("RGB"),
                        "e": Image.open("../assets/e.png").convert("RGB"),
                        "f": Image.open("../assets/f.png").convert("RGB"),}
    self.cache = TransitCache(self.transit, 10)

  @property
  def width(self):
    """Get the display width."""
    if hasattr(self, 'matrix') and self.matrix is not None:
      return self.matrix.width
    else:
      return 128

  @property
  def height(self):
    """Get the display height."""
    if hasattr(self, 'matrix') and self.matrix is not None:
      return self.matrix.height
    else:
      return 32

  def draw_subway_combined(self, id_1, id_2, canvas, duration=15):
    end_time = time.time() + duration

    row_1 = Row(canvas, self.text_font, True, self.width, self.height, self.cache.get(id_1), self.image_cache.get(id_1[0].lower()))
    row_2 = Row(canvas, self.text_font, False, self.width, self.height, self.cache.get(id_2), self.image_cache.get(id_2[0].lower()))

    while time.time() < end_time:
      canvas.Fill(0, 0, 0)

      now = time.time()
      row_1.draw(canvas)
      row_2.draw(canvas)
      canvas = self.matrix.SwapOnVSync(canvas)

      time.sleep(max(0.05 - (time.time() - now), 0))

  def main_control_loop(self, subway_ids):
    canvas = self.matrix.CreateFrameCanvas()
    for id in subway_ids:
      self.cache.register(id)

    while True:
      for i in range(0, len(subway_ids), 2):
        self.draw_subway_combined(id_1=subway_ids[i], id_2=subway_ids[i + 1], canvas=canvas, duration=15)      

    

manager = Manager()
manager.main_control_loop(["F14N", "F14S", "135N", "135S"])

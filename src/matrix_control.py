from flask import Flask, render_template, request
import threading
import os
if os.getenv("EMULATOR", "false") == "true": # change this before pushing
  from RGBMatrixEmulator import RGBMatrix, RGBMatrixOptions, graphics
else:
  from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

# ---- Initialize matrix ----
options = RGBMatrixOptions()
options.rows = 32
options.cols = 128
options.gpio_slowdown = 4
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = "adafruit-hat"

matrix = RGBMatrix(options=options)

# Shared brightness state
brightness = 50

# ---- Flask app ----
app = Flask(__name__)

@app.route("/")
def index():
  # Simple page with slider
  return render_template("index.html", brightness=brightness)

@app.route("/set_brightness", methods=["POST"])
def set_brightness():
  global brightness
  try:
    brightness = int(request.form.get("brightness", 50))
    # Map 0-100 slider to 0-100 for matrix.SetBrightness
    matrix.brightness = brightness
    print(f"Brightness set to {brightness}")
    return "ok", 200
  except Exception as e:
    return str(e), 400

# ---- Optional: a simple test pattern loop ----
def run_matrix_loop():
  canvas = matrix.CreateFrameCanvas()
  offset = 0
  while True:
    for x in range(matrix.width):
      for y in range(matrix.height):
        r = int(((x + offset) % matrix.width) / matrix.width * 255)
        g = int((y / matrix.height) * 255)
        b = 128
        canvas.SetPixel(x, y, r, g, b)
    canvas = matrix.SwapOnVSync(canvas)
    offset += 1

# ---- Start matrix loop in a thread ----
threading.Thread(target=run_matrix_loop, daemon=True).start()

# ---- Run Flask app ----
if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5001)
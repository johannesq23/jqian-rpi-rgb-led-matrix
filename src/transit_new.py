import requests
from collections import defaultdict
from typing import Literal
from datetime import datetime, timezone

class TransitClient:
  def __init__(self, base_url):
    self.base_url = base_url.rstrip("/")

  def fetch_data(self, station_id):
    """Fetch raw API data."""
    url = f"{self.base_url}/by-id/{station_id}"
    response = requests.get(url, timeout=5)
    response.raise_for_status()
    return response.json()

  def get_transit(self, input):
    """
    ("id", "dir", ["station1", "station2"])
    """

    station_id, dir, lines = input
    
    data = self.fetch_data(station_id).get("data", [])
    if len(data) < 1:
      raise RuntimeError("Length of Data < 1")
    data = data[0]

    cleaned_data = defaultdict(lambda: defaultdict(list))

    for stop in data["N"]:
      cleaned_data["N"][stop["route"]].append(stop["time"])
    for stop in data["S"]:
      cleaned_data["S"][stop["route"]].append(stop["time"])

    output = []
    for line in lines:
      for data in cleaned_data[dir][line]:
        dt = datetime.fromisoformat(data)
        now = datetime.now(dt.tzinfo)
        delta = dt - now
        minned = max(0, int(delta.total_seconds() / 60))
        if minned > 7:
          output.append((minned, dir, str.lower(line)))

    return sorted(output)

transit = TransitClient("http://127.0.0.1:5000")
times = transit.get_transit(("229", "N", ["4", "5"]))
print(times)

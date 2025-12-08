import requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import time
import csv

class Transit:
  def __init__(self):
    self.url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm"
    self.id_to_stop_dict = self._load_id_list()
    
  def _load_id_list(self):
    data = {}
    with open("../gtfs_subway/stops.txt", newline="") as f:
      reader = csv.DictReader(f)
      for row in reader:
        row_dict = dict(row)
        data[row_dict.get("stop_id", "")] = row_dict.get("stop_name", "")
    return data

  def get_stop_by_id(self, id: str):
    return self.id_to_stop_dict[id]

  def get_times_by_id(self, id: str):
    # Fetch the feed
    resp = requests.get(self.url)

    # Parse protobuf
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)

    # Convert to dict for easier access (optional)
    feed_dict = MessageToDict(feed)

    # Collect departures
    departures = []

    for entity in feed_dict.get("entity", []):
      trip_update = entity.get("tripUpdate", {})
      if not trip_update:
        continue
      trip_id = trip_update.get("trip", {}).get("tripId", "unknown")
      route_id = trip_update.get("trip", {}).get("routeId")
      
      stop_time_update = trip_update.get("stopTimeUpdate", [])
      for stu in stop_time_update:
        stop_id = stu.get("stopId")
        if stop_id == id:
          departure = stu.get("departure", {}).get("time")
          last_stop_id = self.id_to_stop_dict.get(stop_time_update[-1].get("stopId", ""), "")
          
          # convert to human-readable
          if departure:
            departure_time = time.strftime('%H:%M:%S', time.localtime(int(departure)))
            time_till_departure = max((int(departure) - int(time.time())) // 60, 0)
          else:
            departure_time = None
            time_till_departure = None
            
          departures.append({
            "trip_id": trip_id,
            "route": route_id,
            "departure_time": str(departure_time),
            "time_till_departure_mins": str(time_till_departure),
            "final_stop": last_stop_id
          })

    return departures


# transit = Transit()
# times = transit.get_times_by_id("F14N")
# for entry in times:
#   print(entry)

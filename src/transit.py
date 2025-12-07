import requests
from google.transit import gtfs_realtime_pb2
from google.protobuf.json_format import MessageToDict
import time

class Transit:
  def __init__(self):
    self.url = "https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-bdfm"

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
      
      for stu in trip_update.get("stopTimeUpdate", []):
        stop_id = stu.get("stopId")
        if stop_id == id:
          departure = stu.get("departure", {}).get("time")
          
          # convert to human-readable
          if departure:
            departure_time = time.strftime('%H:%M:%S', time.localtime(int(departure)))
            time_till_departure = (int(departure) - int(time.time())) // 60
          else:
            departure_time = None
            time_till_departure = None
            
          departures.append({
            "trip_id": trip_id,
            "route": route_id,
            "departure_time": departure_time,
            "time_till_departure_mins": time_till_departure
          })

    return departures
  
  def get_next_two_times_by_id(self, id: str):
    return self.get_times_by_id(id)[:2]


transit = Transit()
transit.get_times_by_id("F14N")
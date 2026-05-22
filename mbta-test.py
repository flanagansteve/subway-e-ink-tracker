from subway_service import subway_service, MBTAService, TransitService
from config import config
from datetime import datetime

service = subway_service
trains = service.get_upcoming_trains()

api_name = "Transit" if isinstance(service, TransitService) else "MBTA"
print(f"[{api_name} API] Fetched {len(trains)} predictions at {datetime.now().strftime('%H:%M:%S')}\n")

for route_id in config.MBTA_ROUTES:
    label = config.MBTA_ROUTE_LABELS[route_id]
    route_trains = [t for t in trains if t.route_id == route_id]
    inbound  = [t for t in route_trains if t.direction_id == 1]
    outbound = [t for t in route_trains if t.direction_id == 0]

    print(f"[{label}] {route_id}")
    ib_mins = [t.minutes_until_arrival for t in inbound[:5]]
    ob_mins = [t.minutes_until_arrival for t in outbound[:5]]
    print(f"  IB: {ib_mins or ['—']} min")
    print(f"  OB: {ob_mins or ['—']} min")

print("\nScript execution complete.")

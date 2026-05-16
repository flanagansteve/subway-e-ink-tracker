import logging
from datetime import datetime
from typing import List, Optional, Callable
from dataclasses import dataclass
import requests
import time
import threading
from config import config

logger = logging.getLogger(__name__)


@dataclass
class TrainArrival:
    minutes_until_arrival: int
    arrival_time: str
    train_id: str
    route_id: str
    direction_id: int
    direction_label: str

    def __eq__(self, other):
        if not isinstance(other, TrainArrival):
            return False
        return (self.minutes_until_arrival == other.minutes_until_arrival and
                self.train_id == other.train_id)


class MBTAService:
    BASE_URL = "https://api-v3.mbta.com"

    def __init__(self):
        logger.info("Initializing MBTAService")
        self._subscribers: List[Callable[[List[TrainArrival]], None]] = []
        self._update_thread: Optional[threading.Thread] = None
        self._should_run = False
        self._current_trains: List[TrainArrival] = []

    def subscribe(self, callback: Callable[[List[TrainArrival]], None]):
        self._subscribers.append(callback)
        if self._current_trains:
            callback(self._current_trains)

    def start_updates(self, interval_seconds: int = 15):
        if self._update_thread and self._update_thread.is_alive():
            logger.warning("Update thread already running")
            return
        self._should_run = True
        self._update_thread = threading.Thread(
            target=self._update_loop, args=(interval_seconds,), daemon=True
        )
        self._update_thread.start()
        logger.info(f"Started MBTA update thread with {interval_seconds}s interval")

    def stop_updates(self):
        self._should_run = False
        if self._update_thread:
            self._update_thread.join()
            self._update_thread = None
        logger.info("Stopped MBTA updates")

    def _should_notify(self, new_trains: List[TrainArrival]) -> bool:
        if not self._current_trains or not new_trains:
            return True
        for i in range(min(2, len(new_trains))):
            if i >= len(self._current_trains):
                return True
            if new_trains[i] != self._current_trains[i]:
                return True
        return False

    def _update_loop(self, interval_seconds: int):
        while self._should_run:
            try:
                new_trains = self.get_upcoming_trains()
                if self._should_notify(new_trains):
                    self._current_trains = new_trains
                    self._notify_subscribers(new_trains)
                time.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in update loop: {e}")
                time.sleep(interval_seconds)

    def _notify_subscribers(self, trains: List[TrainArrival]):
        for subscriber in self._subscribers:
            try:
                subscriber(trains)
            except Exception as e:
                logger.error(f"Error notifying subscriber: {e}")

    def get_upcoming_trains(self) -> List[TrainArrival]:
        arrivals = []
        seen = set()
        for stop_id in config.MBTA_STOPS:
            try:
                r = requests.get(
                    f"{self.BASE_URL}/predictions",
                    params={"filter[stop]": stop_id, "api_key": config.MBTA_API_KEY, "page[limit]": 10},
                    timeout=10,
                )
                r.raise_for_status()
                for pred in r.json().get("data", []):
                    arrival = self._process_prediction(pred)
                    if arrival and arrival.train_id not in seen:
                        arrivals.append(arrival)
                        seen.add(arrival.train_id)
            except Exception as e:
                logger.error(f"Error fetching predictions for stop {stop_id}: {e}")

        return sorted(arrivals, key=lambda x: x.minutes_until_arrival)

    def _process_prediction(self, pred: dict) -> Optional[TrainArrival]:
        try:
            attrs = pred["attributes"]
            time_str = attrs.get("arrival_time") or attrs.get("departure_time")
            if not time_str:
                return None

            arrival_time = datetime.fromisoformat(time_str)
            now = datetime.now(arrival_time.tzinfo)
            minutes = max(0, round((arrival_time - now).total_seconds() / 60))

            route_id = pred["relationships"]["route"]["data"]["id"]
            trip_id = pred["relationships"]["trip"]["data"]["id"]
            direction_id = attrs["direction_id"]
            direction_label = config.MBTA_DIRECTION_LABELS.get(route_id, {}).get(direction_id, "—")

            return TrainArrival(
                minutes_until_arrival=minutes,
                arrival_time=arrival_time.strftime("%I:%M %p"),
                train_id=trip_id,
                route_id=route_id,
                direction_id=direction_id,
                direction_label=direction_label,
            )
        except Exception as e:
            logger.error(f"Error processing prediction: {e}")
            return None


subway_service = MBTAService()

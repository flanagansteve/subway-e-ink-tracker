import os
from dotenv import load_dotenv
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

# Force reload environment variables
load_dotenv(override=True)

@dataclass
class DisplayConfig:
    WIDTH: int = 825
    HEIGHT: int = 1200
    
    def __post_init__(self):
        self.HEADER_HEIGHT = self.HEIGHT // 9 # 1/8th of the height
        self.TRAIN_SECTION_HEIGHT =  (self.HEIGHT * 2) // 3 # ((self.HEIGHT - self.HEADER_HEIGHT) * 2) // 4  # Half the height 
        self.WEATHER_SECTION_HEIGHT = self.HEIGHT - self.HEADER_HEIGHT - self.TRAIN_SECTION_HEIGHT # The rest
        
        # Add vertical lane dimensions
        self.VERTICAL_LANE_WIDTH = self.WIDTH // 3
        self.MAIN_SECTION_WIDTH = self.WIDTH - self.VERTICAL_LANE_WIDTH
        
        # Central column position for train and weather icons
        self.ICON_COLUMN_X = 100 # self.MAIN_SECTION_WIDTH // 6
        
        self.HEADER_Y = 0
        self.TRAIN_SECTION_Y = self.HEADER_HEIGHT
        self.WEATHER_SECTION_Y = self.TRAIN_SECTION_Y + self.TRAIN_SECTION_HEIGHT
        
        # Add vertical lane position
        self.VERTICAL_LANE_X = self.MAIN_SECTION_WIDTH

@dataclass
class WeatherConfig:
    def __init__(self, display: DisplayConfig):
        # Adjust main icon sizes for new layout
        self.MAIN_ICON_SIZE = 165
        self.SMALL_ICON_SIZE = 80 # round(display.WEATHER_SECTION_HEIGHT / 4)
        self.VERTICAL_ICON_SIZE = 165  # New size for vertical lane

        self.CURRENT_X = 20
        self.CURRENT_Y = display.WEATHER_SECTION_Y + 20
        
        # Add vertical lane positions
        self.VERTICAL_CURRENT_Y = display.TRAIN_SECTION_Y + 20
        self.VERTICAL_HOURLY_START_Y = self.VERTICAL_CURRENT_Y + self.VERTICAL_ICON_SIZE + 40
        
        self.FORECAST_Y = self.CURRENT_Y + self.MAIN_ICON_SIZE + 40
        spacing = (display.WIDTH - 60) // 3
        self.TODAY_X = 20
        self.TOMORROW_X = self.TODAY_X + spacing
        self.OVERMORROW_X = self.TOMORROW_X + spacing

@dataclass
class SubwayConfig:
    def __init__(self, display: DisplayConfig):
        self.SECTION_Y = display.TRAIN_SECTION_Y
        self.SECTION_HEIGHT = display.TRAIN_SECTION_HEIGHT
        self.NEXT_TRAIN_Y = self.SECTION_Y + 20
        self.LIST_Y = self.NEXT_TRAIN_Y + 100
        self.PADDING_X = 20

        pass  # Y positions are computed dynamically in layout based on route count

@dataclass
class TimeConfig:
    def __init__(self, display: DisplayConfig, FONT_SIZES):
        self.Y = display.HEADER_Y + (display.HEADER_HEIGHT // 2) - FONT_SIZES['header'] // 2 - 8
        self.X = display.WIDTH // 2

class Config:
    def __init__(self):
        logger.info("Loading configuration from environment variables...")
        self.DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'

        self.MBTA_API_KEY = os.getenv('MBTA_API_KEY')
        if not self.MBTA_API_KEY:
            raise ValueError("MBTA_API_KEY must be set in .env file")

        # Stop IDs to poll for predictions
        self.MBTA_STOPS = [
            'place-harvd',    # Green Line B — Harvard Avenue
            'place-stpul',    # Green Line C — St Paul St
            '1308',           # Route 66 — Harvard St @ Beacon St (inbound toward Harvard)
            '1372',           # Route 66 — Harvard St @ Beacon St (outbound toward Nubian)
            'place-WML-0025', # Framingham/Worcester Line — Lansdowne
        ]

        # Route IDs to display, in order top-to-bottom
        self.MBTA_ROUTES = ['Green-B', 'Green-C', '66', 'CR-Worcester']

        # Short labels shown inside the route circle
        self.MBTA_ROUTE_LABELS = {
            'Green-B': 'B',
            'Green-C': 'C',
            '66': '66',
            'CR-Worcester': 'WR',
        }

        # Human-readable direction labels per route
        self.MBTA_DIRECTION_LABELS = {
            'Green-B':      {0: 'Boston Col', 1: 'Govt Ctr'},
            'Green-C':      {0: 'Clev Cir',   1: 'Pk St'},
            '66':           {0: 'Nubian',      1: 'Harvard'},
            'CR-Worcester': {0: 'Worcester',   1: 'South Sta'},
        }
        
        # Display configurations
        self.display = DisplayConfig()
        self.weather = WeatherConfig(self.display)
        self.subway = SubwayConfig(self.display)
        
        # Font sizes
        self.FONT_SIZES = {
            'small': 16,
            'medium': 20,
            'large': 24,
            'xlarge': 36,
            'xxlarge': 42,
            'header': 60,
            'xheader': 72,
        }

        self.time = TimeConfig(self.display, self.FONT_SIZES)
        
        # Commute time configurations
        self.commute_times = {
            'morning': {
                'start': '07:00',
                'end': '10:00',
                'label': 'Morning Commute'
            },
            'evening': {
                'start': '17:00', 
                'end': '19:00',
                'label': 'Evening Commute'
            }
        }

        # Weather coordinates (Lansdowne/Fenway, Boston)
        self.WEATHER_COORDS = (
            float(os.getenv('WEATHER_LAT', '42.347')),
            float(os.getenv('WEATHER_LON', '-71.100'))
        )

# Create a global configuration instance
config = Config()
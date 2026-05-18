# e-ink Subway & Weather Display
A Raspberry Pi-powered e-ink display showing real-time MBTA arrival times and weather forecasts. Perfect for mounting on your wall to check train times and weather before heading out.

Derived from Sam's NYCT project [here](https://sambroner.com/posts/raspberry-pi-train).

# Features
- Real-time subway arrival times
- Current weather and 3-day forecast
- Debug mode with automatic image preview
- Native e-ink display support on Raspberry Pi

![E-Ink Display Demo](IMG_5573.jpeg)

## Getting Started

### Hardware
- Raspberry Pi 4b+
    - SD Card, power supply, (optionally keyboard, mouse, hdmi cord, etc.)
- [Waveshare 9.7inch E-Ink display HAT for Raspberry Pi](https://www.waveshare.com/product/displays/e-paper/9.7inch-e-paper-hat.htm)
- [Frame](https://www.americanframe.com/natural-cherry-gallery-frame) (optional)
- Custom Mat (Optional, but I got mine from AmericanFrame.com)

### Raspberry Pi Setup
0. Figure out how you're going to connect to the Raspberry Pi
1. Install UV
2. Enable the SPI interface
3. Attach the e-ink display to the Raspberry Pi

To test the display on Raspberry Pi:
```bash
git clone https://github.com/flanagansteve/subway-e-ink-tracker.git
cd subway-eink
uv sync
uv run test.py
```

### Installation
1. Install uv (if not already installed)
2. Install dependencies:
   ```bash
   uv sync
   ```
3. Set up .env file (copy from .env.template)

Running on your wall
1. Set up a systemd service

### Running

If `DEBUG=true` in your .env:
- Images will be saved to `debug_output/current_display.png`
- Your system's default image viewer will automatically open and update with each refresh
- The image viewer will refresh automatically when new data arrives

If `DEBUG=false`:
- On Raspberry Pi: The e-ink display will update
- On other platforms: An error will be raised (e-ink display only works on Raspberry Pi)

To run:
```bash
uv run runner.py
```

## CairoSVG

- CairoSVG is used to convert SVGs to PNGs for the display.
- On mac, you may need to manually compile Cairo: https://stackoverflow.com/questions/36225410/installing-cairo-and-pycairo-mac-osx

## Display Modes
Figuring out the right display mode was annoying. The full spec is [here](https://www.waveshare.net/w/upload/c/c4/E-paper-mode-declaration.pdf).


## To Do
- [ ] Consider checking if the wait time still makes sense and then refresh. E.g. It's 11am. Train Arrives at 11:04 and there's no update. When time turns to 11:01, even if no update, refresh.
- [ ] Fix hourly weather... seems like it's only 100% or zero?
- [ ] Use [Transit's API](https://api-doc.transitapp.com) instead of the raw MBTA API; it'd be a superset of the data the MBTA has, and would include Transit's crowdsourced on-train data.
- [ ] Modify the IB / OB labelling to instead dynamically use each route's terminal - e.g., for the C Line, show Cleveland Circle on one row and Government Center on the other (or an abbreviation)
- [ ] (Non-code) hang the frame up + buy good USB-C cable to make that clean

## Credits
- IT8951 library by GregDMeyer: https://github.com/GregDMeyer/IT8951
- Sam, for the NYCT version: https://github.com/SamBroner/subway-e-ink-tracker. I only barely tweaked it to wrap it around the MBTA API instead.

## Setting up as a service
To have the display start automatically on boot:

```bash
sudo systemctl restart subway-eink.service
sudo systemctl stop subway-eink.service
```

```bash
[Unit]
Description=Subway E-Ink Display Service
After=network.target

[Service]
Type=simple
User={your username}
WorkingDirectory=/path/to/repo
ExecStart=/path/to/uv run runner.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

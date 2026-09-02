### soko

A real-time flight tracker and radar for RGB LED Matrix Panels, written using CircuitPython. Select a single callsign to follow an individual aircraft, or let it scan the sky overhead and cycle through whatever is nearby. 

#### What it shows

There are two modes which you can choose:

**Flight mode** follows one callsign. The airline logo sits on the left with teh callsign, route and aircraft type beside it. Below this sits a status or what the flight is currently doing such as if it's on the ground, how long since deparature and how long remains. This is followed with a progress bar that fills as the aircraft covers the distance between its origin and destination.

**Radar mode** watches for all flights within a radius of your location and rotates through the aircraft inside it every ten seconds, nearest first. Each one shows its route with origin and destination cities, plus range and bearing from the device. 

#### Hardware

As long as you can get a Matrix Panel running, you will be able to run this repository. But specific of what I used are:
- Any RGB Matrix Panel, I used a [high resolution 128x64 one.](https://s.click.aliexpress.com/e/_c3mOT811)
- A CircuitPython board with an HUB75 interface, I used a [MatrixPortal S3](https://s.click.aliexpress.com/e/_c4bPcamx)
- A 5V supply.

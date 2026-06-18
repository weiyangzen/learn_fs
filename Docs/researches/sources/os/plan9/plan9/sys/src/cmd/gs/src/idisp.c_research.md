# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/idisp.c

Implements display-device callback installation. `display_set_callback` runs a small PostScript snippet to check whether `devicedict /display` exists and retrieves the display device if present.

If the device exists:
- verifies stack result types
- closes the device if already open
- sets `gx_device_display.callback`
- reopens the device if it was open
- cleans stack entries

Harmless when the display device is not compiled in. This bridges the public API display callback into the actual display device instance.

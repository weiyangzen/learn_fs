# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/idisp.c

Implements display-device callback installation for the interpreter API.

Key behavior:
- `display_set_callback` runs PostScript to test whether `devicedict /display` exists and retrieve the display device.
- If present, verifies stack types, gets the device, closes it if already open, installs the callback pointer in `gx_device_display`, and reopens it if needed.
- Pops the temporary device and boolean results from the operand stack.
- Returns success when display device is absent.

Research notes:
- This is only used when `gsapi_set_display_callback` is called and the display device is included.
- It bridges API-level display callbacks into the actual device instance after initialization.

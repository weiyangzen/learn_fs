# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/main.c

Command entry point for `usb/ether`.

Behavior:
- Parses top-level options: `-a` MAC override, `-D` USB filesystem debug, `-d` USB debug, `-N` device number override, `-m` mountpoint, and `-s` service name.
- Builds an argument string passed into each device worker.
- Matches candidate devices via `matchether`, accepting communication-class devices or devices listed in `cinfo[]`.
- Initializes the USB file directory service at `/net` by default using `usbfsinit`.
- Calls `startdevs` to open/configure matching USB devices and run `ethermain`.

This file is thin orchestration; actual packet/file handling is in `ether.c`.

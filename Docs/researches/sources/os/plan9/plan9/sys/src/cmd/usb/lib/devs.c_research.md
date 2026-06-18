# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/lib/devs.c

Device discovery and per-device worker launcher for standalone USB drivers.

Key functions:
- `matchdevcsp` matches text from `/dev/usb/*/ctl` against requested CSP values.
- `finddevs` scans `/dev/usb`, reads endpoint zero control files, and returns enabled idle devices matching a predicate.
- `startdevs` binds `#u` if needed, opens/configures explicit or discovered devices, then starts a `workproc` for each successful device.
- `workproc` tokenizes driver arguments and invokes the supplied device main function.

Behavior:
- Supports both explicit device path arguments and automatic discovery.
- Uses a channel to wait for worker startup success/failure.
- Closes devices on failed driver initialization.

This is the common launcher used by `usb/ether`, `usb/kb`, `usb/serial`, and `usb/print`.

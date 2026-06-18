# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/main.c

Command entry point for USB serial devices.

Behavior:
- Matches devices through `uconsmatch`, `plmatch`, `ftmatch`, or `slmatch`.
- Parses `-D` USB filesystem debug, `-d` USB debug, `-N` device number, `-m` mountpoint, and `-s` service name.
- Initializes USB directory file server mounted at `/dev` by default.
- Calls `startdevs` to run `serialmain` for matching devices.

It only handles discovery and setup; common serial file implementation is in `serial.c`.

# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/print/main.c

Command entry point for USB printer support.

Behavior:
- Matches printer-class devices with CSP `0x020107`.
- Parses `-d` USB debug and `-N` device number override.
- Builds worker arguments and invokes `startdevs` with `printmain`.
- Installs `%U` formatting and starts each matching device.

Actual endpoint setup is in `print.c`.

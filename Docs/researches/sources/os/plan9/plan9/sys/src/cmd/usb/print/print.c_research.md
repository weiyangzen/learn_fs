# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/print/print.c

USB printer endpoint binder.

Main behavior:
- `findendpoints` scans parsed USB endpoints for a printer interface CSP and bulk OUT endpoint.
- Opens the bulk OUT endpoint, opens its data file for writing, optionally enables debug, and names it `lp%d`.
- `printmain` parses `-N`, then calls `findendpoints`.

Despite enum qid constants, this file does not implement its own file server; it configures the kernel USB endpoint as a printer-like output device.

Known limitation:
- Header comment notes it assumes the printer remains connected and is not hot-plugged.

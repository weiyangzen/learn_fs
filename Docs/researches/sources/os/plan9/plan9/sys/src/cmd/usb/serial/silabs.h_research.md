# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/silabs.h

Tiny Silabs serial backend header.

Exports:
- `Serialops slops`
- `slmatch(char *info)`

Used by `serial/main.c` and `serial.c` for CP210x matching and operation dispatch.

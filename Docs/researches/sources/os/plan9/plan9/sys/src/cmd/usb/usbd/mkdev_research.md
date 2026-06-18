# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/usbd/mkdev

rc/awk generator for `Devtab` entries from `usbdb`.

Behavior:
- Reads class constants from `../lib/usb.h` and builds sed substitutions from class names to numeric constants.
- Emits C includes and extern declarations for embedded driver `*main` functions.
- Parses `embed` and `auto` sections in `usbdb`.
- Emits `Devtab devtab[]` entries with driver name, embedded init or `nil`, CSP/class/subclass/proto match fields, VID/DID, and args.
- Pads CSP arrays to four entries.
- Terminates table with a nil entry.

This script generates machine-maintained USB daemon driver matching code.

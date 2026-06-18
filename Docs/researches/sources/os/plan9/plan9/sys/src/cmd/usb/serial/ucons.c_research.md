# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ucons.c

Backend for Ajays Net20DC USB debug cable / console-like serial device.

Behavior:
- Defines `uconsinfo[]` with Net20DC VID/DID.
- `uconsmatch` matches device info text against that table.
- `ucseteps` marks the port as non-real baud (`~0`), limits max transfers to 8 bytes, and sets endpoint max packet size to 8.
- `uconsops` only supplies `seteps`; all other serial operations are no-ops/defaults.

This is a minimal adapter for a special USB debug cable rather than a full UART chip.

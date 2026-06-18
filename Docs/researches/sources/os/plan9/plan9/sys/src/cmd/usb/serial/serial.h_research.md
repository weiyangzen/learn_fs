# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/serial.h

Shared declarations for USB serial drivers.

Defines:
- `Serialops`, the chip-specific operation table.
- `Serialport`, per-interface state including endpoints, embedded `Usbfs`, line settings, modem/error counters, channels, and data buffering.
- `Serial`, whole-device state including `Dev`, chip type, recovery state, operation table, interface count, packet sizes, FTDI header sizes, and baud base.
- Common control constants such as software flow characters and RTS/DTR bits.
- `Cinfo` VID/DID/controller record.
- Exports common entry points and helpers: `serialmain`, `serialrecover`, `serialreset`, `serdumpst`, and global debug/device tables.

This header is the contract between the common serial layer and chip backends.

# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/ether/ether.h

Shared declarations for the USB Ethernet driver family.

Defines:
- Controller IDs: CDC, ASIX variants, and SMSC LAN95xx.
- Ethernet constants such as address length, packet length, header size, max packet size, connection count, and buffer count.
- USB CDC Ethernet descriptor constants.
- `Buf`, the receive/transmit buffer with header slack and payload pointer.
- `Conn`, the per-open ether connection, including packet type filtering, header-only mode, promiscuous flag, and receive channel.
- `Etherops`, the controller-specific operations table.
- `Ether`, the main device state containing USB endpoints, MAC address, counters, queues, operation hooks, and embedded `Usbfs`.
- `Cinfo`, the VID/DID/controller mapping record.
- `Etherpkt`, a minimal Ethernet frame header layout.

Exports:
- `ethermain`, controller reset hooks, `parseaddr`, and `dumpframe`.
- Global `cinfo[]` and `etherdebug`.
- `deprint` debug macro.

This header is the contract between the generic Ethernet file server and hardware-specific backends such as SMSC and ASIX.

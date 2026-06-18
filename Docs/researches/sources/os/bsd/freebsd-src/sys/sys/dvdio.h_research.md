# File Research: sources/os/bsd/freebsd-src/sys/sys/dvdio.h

## Purpose
Defines DVD authentication and structure-read ioctl ABI.

## Main Elements
- `struct dvd_layer` describes physical layer fields and sector ranges.
- `struct dvd_struct` carries read-structure format, layer, flags, length, and 2048-byte data buffer.
- `struct dvd_authinfo` carries CSS/RPC authentication state, region fields, LBA, and key/challenge bytes.
- Constants name DVD structure formats, report-key formats, send-key formats, and invalid AGID.
- Ioctls: `DVDIOCREPORTKEY`, `DVDIOCSENDKEY`, `DVDIOCREADSTRUCTURE`.

## Dependencies And Integration
Used by optical media drivers and userland DVD tools.

## Risk Notes
The ABI uses C bitfields, so it is compiler/layout sensitive within the supported platform ABI. Authentication data sizes are fixed and must be copied carefully.

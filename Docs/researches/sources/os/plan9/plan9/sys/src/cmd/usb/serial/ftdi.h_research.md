# File Research: sources/os/plan9/plan9/sys/src/cmd/usb/serial/ftdi.h

FTDI constants and declarations.

Contents:
- Extensive VID/DID constants for FTDI and FTDI-based devices.
- FTDI command request constants for reset, modem control, flow control, baud rate, data parameters, status, latency timer, bit mode, EEPROM access, and pins.
- Port/interface constants and request type bit.
- Chip type constants: SIO, FT8U232AM, FT232BM, FT2232C, FTKINDR, FT2232H, FT4232H.
- Legacy SIO baud selector constants.
- Data/parity/stop/break bit encodings.
- Flow-control encodings.
- Bitbang/MPSSE mode constants.
- FTDI input status header bit definitions and output header fields.
- Exports `ftops` and `ftmatch`.

This header is mostly device database and protocol definitions consumed by `ftdi.c`.

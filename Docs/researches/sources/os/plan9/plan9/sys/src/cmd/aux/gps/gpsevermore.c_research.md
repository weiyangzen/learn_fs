# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/gps/gpsevermore.c

This file initializes/configures EverMore GPS receivers over a serial line.

Key behavior:
- Opens a serial data file and matching control file.
- Sets baud and serial framing.
- Builds EverMore binary packets with DLE escaping and checksum.
- Sends an initialization packet containing GPS week/time, approximate location, altitude, datum, warm start, NMEA output mask, and baud selector.
- Contains helpers for baud and message-output configuration packets.

Important details:
- Default serial device is `/dev/eia0`.
- Position can be supplied with `-l`.
- `-n` chooses a new receiver baud rate while `-b` chooses current line baud.
- Uses shared GPS coordinate parsing and `%L` formatting.

Filesystem relevance:
- Indirect: controls serial device files used by GPS hardware.

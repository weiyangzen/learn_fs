# File Research: sources/os/plan9/9front/sys/src/cmd/aux/gps/gpsevermore.c

Role: Initialization/configuration utility for EverMore GPS receivers.

Behavior:
- Opens the serial device (default `/dev/eia0`) and optionally configures its control file using a baud format string.
- Builds EverMore binary packets with DLE byte-stuffing, length byte, checksum, DLE/STX header, and DLE/ETX trailer.
- Sends message `0x80` with current GPS week/seconds, position hint, altitude, datum, warm-start mode, NMEA message mask, and baud selection.
- Defines helpers for messages `0x89` and `0x8e`, but `main` only calls `evermore80`.

Options:
- `-b baud`, `-d device`, `-l longitude latitude`, `-n newbaud`, `-D`.
- Default position is near New York City; location parsing uses `strtolatlon`.

Integration:
- Uses shared `%L` place formatter and `Place` parsing from GPS utilities.

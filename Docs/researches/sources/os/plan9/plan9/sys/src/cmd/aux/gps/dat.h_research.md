# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/gps/dat.h

This header defines shared GPS utility types and prototypes.

Key behavior:
- Defines `Place` with longitude and latitude.
- Defines `Undef` and default NMEA baud rate `Baud`.
- Declares `nowhere`, `debug`, `%L` formatter support, and coordinate parsers.

Filesystem relevance:
- Supporting header for GPS utilities and `gpsfs`.

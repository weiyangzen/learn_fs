# File Research: sources/os/plan9/9front/sys/src/cmd/aux/gps/dat.h

Role: Shared GPS type and declarations.

Contents:
- Defines `Place` with `lon` and `lat` doubles.
- Declares `%L` formatting pragma for `Place`.
- Defines `Undef` sentinel and default NMEA baud rate `Baud = 4800`.
- Declares shared globals and helpers: `nowhere`, `debug`, `placeconv`, `strtopos`, and `strtolatlon`.

Use:
- Included by `gpsfs.c`, `gpsevermore.c`, and `util.c`.

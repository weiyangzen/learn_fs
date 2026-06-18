# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/gps/gpsfs.c

This file implements `gpsfs`, a 9P filesystem exposing live GPS data.

Key behavior:
- Creates `/gps/time`, `/gps/position`, `/gps/satellites`, `/gps/stats`, and `/gps/raw`.
- Opens and configures a serial GPS stream.
- Background parser reads NMEA lines, checks checksums, parses common GPS sentence types, and updates the current fix.
- Exposes formatted current fix, time correlation, satellite table, parser statistics, and raw line ring buffer.
- Can periodically correct `#r/rtc` from GPS time.

Important details:
- Supports GGA, GLL, GSA, GSV, RMC, VTG, and some Rockwell/Astral proprietary messages.
- Maintains validation counters for bad/good/suspect latitude, longitude, and time.
- Raw buffer is 64 KiB and read through exclusive `raw` file mode.
- Estimates first-character timestamp from serial baud and bytes read.
- If serial control open fails, marks output as playback/invalid.

Filesystem relevance:
- Direct: synthetic 9P namespace translating serial GPS data into readable files.

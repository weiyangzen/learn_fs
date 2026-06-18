# File Research: sources/os/plan9/9front/sys/src/cmd/aux/gps/gpsfs.c

Role: 9P GPS filesystem that reads NMEA serial data and exposes current fix, satellites, stats, and raw stream.

Filesystem:
- Builds an in-memory lib9p tree with `/gps/time`, `/gps/position`, `/gps/satellites`, `/gps/stats`, and exclusive `/gps/raw`.
- Default srv name is `gps`, mount point `/mnt`, serial device `/dev/eia0`, baud 4800.

Reader pipeline:
- `gpsinit` starts `gpstrack`, which configures the serial line, reads NMEA lines, validates checksums, tokenizes by comma/CR/LF, and updates a local `Fix`.
- When a fix is marked valid, it copies it into global `curfix` under `fixlock`, increments sample count, resets per-message state, and optionally sleeps in playback mode.

Supported messages:
- Handles ASTRAL query replies, proprietary Rockwell messages, GPGGA, GPRMC, GPGSA, GPGLL, GPGSV, and GPVTG.
- Parses time/date, latitude/longitude, altitude, sea level, satellites, dilution values, speed, course, heading, and magnetic variation.

Data quality:
- Rejects bad or suspicious latitude, longitude, and time jumps using counters and a short tolerance window.
- Can set the RTC with `-r` via shared `rtcset`.

Raw/stat support:
- Maintains a 64 KiB raw ring buffer and per-read offsets.
- Tracks checksum errors, per-message format errors, serial read-size histogram, bad/good/suspect coordinate counters, and processed sample count.

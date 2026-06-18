# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_msts.c

TTY line discipline that decodes Meinberg Standard Time String data and exposes time/signal sensors.

Data model:
- `struct msts` stores a sentence buffer, time and signal sensors, sensor device identity, timestamp/gap tracking, timeout state, last decoded time, sync state, input position, and PPS-missing flag.

Open/close:
- `mstsopen()` requires superuser, allocates state, initializes sensors, sets sync mode to wait for STX, delegates base tty open, installs the sensor device, and sets a timeout.
- `mstsclose()` restores `TTYDISC`, deletes timeout, deinstalls sensors, frees state, and delegates base tty close.

Input and parsing:
- `mstsinput()` starts a sentence at ASCII STX, ends at ETX, records best available timestamp, validates optional tty PPS/modem timestamp proximity, scans completed sentences, and still passes bytes to termios.
- `msts_scan()` splits fields on semicolons.
- `msts_decode()` validates field count, parses date/time, applies CET/CEST offset based on status field, checks monotonicity, computes timedelta, updates signal/time status, and arms the trust timeout only for valid status.

Conversion helpers:
- `msts_date_to_nano()` converts `D:DD.MM.YY` to epoch nanoseconds.
- `msts_time_to_nano()` converts `U:HH.MM.SS` to nanoseconds since midnight with digit-by-digit bounds.

Sensor degradation:
- `msts_timeout()` degrades time status from OK to WARN and then CRIT if valid strings stop arriving.
- Requested tty timestamping without PPS sets time status critical.

Filesystem/storage relevance:
- No filesystem logic. Relevant as tty line-discipline parsing and kernel sensor publication for serial time devices.

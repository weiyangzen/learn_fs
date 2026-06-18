# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_nmea.c

TTY line discipline that decodes NMEA 0183 GNSS serial data and exposes time, signal, position, altitude, and speed sensors.

Data model:
- `struct nmea` stores an NMEA sentence buffer, sensors for timedelta/signal/latitude/longitude/altitude/speed, sensor-device identity, timestamp/gap tracking, trust timeout, last decoded time, sync state, PPS-missing state, and current GPS mode.

Open/close:
- `nmeaopen()` requires superuser, allocates per-tty state, initializes all sensors as unknown/invalid, attaches them to a sensor device, delegates base tty open, installs the sensor device, and sets a timeout.
- `nmeaclose()` restores `TTYDISC`, removes timeout and sensors, frees state, resets instance numbering when appropriate, and delegates base close.

Input and parsing:
- `nmeainput()` starts collection at `$`, ends at CR or LF, records the best timestamp, optionally compares tty PPS/modem timestamps, and passes all bytes to the termios discipline.
- `nmea_scan()` splits fields, computes and validates optional checksum, filters known GNSS talkers (`BD`, `GA`, `GL`, `GN`, `GP`), and dispatches only `RMC` and `GGA` sentences.
- `nmea_gprmc()` decodes time/date, fix status, mode, latitude, longitude, and ground speed.
- `nmea_decode_gga()` decodes altitude from GPS fix data.

Conversion helpers:
- `nmea_atoi()` parses decimal numeric fields to fixed thousandths.
- `nmea_degrees()` converts NMEA degree-minute coordinates to angle sensor units.
- `nmea_date_to_nano()` converts `DDMMYY` to epoch nanoseconds.
- `nmea_time_to_nano()` converts `HHMMSS[.fraction]` to nanoseconds since midnight.

Sensor behavior:
- Valid RMC fix status marks time, signal, latitude, longitude, and speed OK and clears invalid flags.
- Void status marks signal critical and location/speed warning.
- GGA altitude clears altitude invalid flag when parsed.
- Timeout marks signal critical and degrades or invalidates all exposed sensors.
- Missing PPS when timestamping was requested marks time critical.

Filesystem/storage relevance:
- No filesystem logic. Relevant as a tty line discipline that turns character-device serial input into kernel sensor state while preserving normal termios input flow.

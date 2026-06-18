# File Research: sources/os/bsd/openbsd-src/sys/kern/tty_endrun.c

TTY line discipline that decodes EndRun Technologies native time-of-day serial messages and exports kernel sensors.

Data model:
- `struct endrun` contains a fixed receive buffer, time and signal sensors, sensor device identity, current and last timestamps, timeout state, sentence gap tracking, last decoded time, sync state, buffer position, and PPS-missing state.

Open/close:
- `endrunopen()` requires superuser, allocates per-tty state, initializes a timedelta sensor and signal sensor, attaches sensors, delegates base tty open to `TTYDISC`, installs a timeout, and stores state in `tp->t_sc`.
- `endrunclose()` switches back to `TTYDISC`, removes timeout and sensors, frees state, resets instance numbering when last instance closes, and delegates base close.

Input and parsing:
- `endruninput()` collects fixed-length EndRun messages ending in CRLF, treats the character after LF as the on-time TFOM character, captures the best timestamp, checks optional tty PPS/modem timestamps, and passes all input through to the normal termios discipline.
- `endrun_scan()` splits the sentence into fields.
- `endrun_decode()` validates field count, date, time, optional local-time offset, monotonicity, TFOM, and PPS state; then updates sensor timedelta and signal status.

Conversion helpers:
- `endrun_atoi()` validates fixed-width decimal strings.
- `endrun_date_to_nano()` converts year plus day-of-year to nanoseconds since the epoch.
- `endrun_time_to_nano()` converts `HH:MM:SS`.
- `endrun_offset_to_nano()` converts signed half-hour UTC offsets for local mode.

Sensor degradation:
- `endrun_timeout()` degrades the time sensor from OK to WARN and then CRIT when valid strings stop arriving.
- TFOM values 6/7/8 are OK, 9 warns, invalid TFOM is critical; timestamping requested without detected PPS marks the time sensor critical.

Filesystem/storage relevance:
- No filesystem logic. Relevant as a specialized tty line discipline using character-device input, tty timestamp flags, and kernel sensor registration.

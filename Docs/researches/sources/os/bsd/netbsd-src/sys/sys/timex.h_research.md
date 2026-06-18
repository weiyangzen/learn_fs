# File Research: sources/os/bsd/netbsd-src/sys/sys/timex.h

Read completely: 264 lines.

Defines the NTP precision time user/kernel interface.

Key elements:
- Sets `NTP_API` version 4 and NTP discipline constants such as `MAXPHASE`, `MAXFREQ`, `MINSEC`, `MAXSEC`, and `NANOSECOND`.
- Defines `MOD_*` control mode bits for `ntp_adjtime`.
- Defines `STA_*` status bits for PLL/FLL, PPS discipline, leap seconds, sync state, resolution, and clock source.
- Defines clock states `TIME_OK`, `TIME_INS`, `TIME_DEL`, `TIME_OOP`, `TIME_WAIT`, and `TIME_ERROR`.
- `struct ntptimeval` reports current time, maximum/estimated error, TAI offset, and time status.
- `struct timex` controls and reports clock offset, frequency, errors, status, time constant, precision, tolerance, and PPS statistics.
- Kernel declarations include `ntp_update_second`, `ntp_adjtime1`, `ntp_gettime`, and `ntp_timestatus`.
- Userland declarations expose `ntp_gettime` and `ntp_adjtime`.

Risks and notes:
- Unit interpretation changes with `STA_NANO`, so daemon/kernel agreement is critical.
- Status bits include read-only fields; callers must not expect to set `STA_RONLY`.

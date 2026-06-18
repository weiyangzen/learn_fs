# File Research: sources/os/bsd/freebsd-src/sys/sys/timex.h

Network Time Protocol kernel discipline ABI header.

Key responsibilities:
- Defines NTP API version and kernel discipline constants for maximum phase/frequency error, PLL/FLL interval limits, nanosecond scale, scaled PPM, and max time constant.
- Defines `timex.modes` control bits for offset, frequency, max/estimated error, status, time constant, PPS max, TAI, micro/nano resolution, and clock A/B selection.
- Defines status bits for PLL/FLL, PPS discipline, leap insert/delete, unsynchronized state, PPS faults, hardware fault, resolution, mode, and clock source.
- Defines clock state constants for `ntptimeval.time_state`.
- Defines `struct ntptimeval` for `ntp_gettime` and `struct timex` for `ntp_adjtime`, including PPS statistics fields.
- Declares kernel `ntp_update_second()` or userland `ntp_adjtime()`/`ntp_gettime()` on FreeBSD.

Dependencies:
- Includes `_timespec` on FreeBSD and `sys/cdefs.h` for userland declarations.

Notable risks:
- Units for several fields depend on `STA_NANO`; callers must not assume all offsets/jitter are always nanoseconds.
- Read-only status bits are explicitly masked by `STA_RONLY` and should not be accepted as daemon-controlled input.

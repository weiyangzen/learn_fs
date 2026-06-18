# File Research: sources/os/bsd/dragonflybsd/sys/sys/timex.h

NTP precision time discipline ABI.

Key contents:
- Defines `NTP_API` version 4.
- Includes `sys/syscall.h` and `sys/time.h`.
- Defines NTP discipline bounds:
  - `MAXPHASE`
  - `MAXFREQ`
  - `MINSEC`
  - `MAXSEC`
  - `NANOSECOND`
  - `SCALE_PPM`
  - `MAXTC`
- Defines `MOD_*` control bits for `timex.modes`.
- Defines `STA_*` status bits for PLL/FLL, PPS, leap second, sync, resolution, mode, and clock source.
- Defines read-only status mask `STA_RONLY`.
- Defines clock state constants `TIME_OK` through `TIME_ERROR`.
- Defines `struct ntptimeval` for `ntp_gettime`.
- Defines `struct timex` for `ntp_adjtime`.
- DragonFly-specific declarations:
  - kernel `ntp_update_second`
  - userland `ntp_adjtime`
  - userland `ntp_gettime`

Important behavior:
- Time offset/precision/jitter fields are interpreted as microseconds or nanoseconds depending on `STA_NANO`.
- Read-only PPS fields are present regardless of kernel PPS configuration for portability.
- Frequency is expressed as scaled PPM.

Research notes:
- This is public ABI for NTP daemons and kernel clock discipline.
- The comments document the historical microsecond-to-nanosecond transition and compatibility expectations.

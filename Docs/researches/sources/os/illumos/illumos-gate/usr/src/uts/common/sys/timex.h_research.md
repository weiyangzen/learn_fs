# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/timex.h

## Purpose
Network Time Protocol clock discipline interface and kernel timing parameter definitions.

## Main Interfaces
- Defines PLL/FLL scaling constants, phase/frequency limits, PPS averaging/watchdog constants, and leap status values.
- Defines mode flags such as `MOD_OFFSET`, `MOD_FREQUENCY`, `MOD_MAXERROR`, `MOD_ESTERROR`, `MOD_STATUS`, `MOD_TIMECONST`, `MOD_CLKA`, and `MOD_CLKB`.
- Defines status flags such as `STA_PLL`, `STA_PPSFREQ`, `STA_PPSTIME`, `STA_FLL`, `STA_INS`, `STA_DEL`, `STA_UNSYNC`, and read-only PPS/error bits.
- Defines `struct ntptimeval`, `struct ntptimeval32`, and `struct timex`.
- Declares `ntp_gettime` and `ntp_adjtime`.
- Kernel declarations include `clock_update` and `ddi_hardpps`.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/time.h`, `sys/syscall.h`, and `sys/inttypes.h`. It supports NTP adjustment syscalls and kernel hard-PPS discipline.

## Research Notes
The file encodes illumos’ NTP discipline ABI. Consumers should distinguish writable adjustment modes from read-only status/error bits.

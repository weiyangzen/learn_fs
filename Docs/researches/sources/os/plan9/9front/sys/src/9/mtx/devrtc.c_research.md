# File Research: sources/os/plan9/9front/sys/src/9/mtx/devrtc.c

This file implements the MTX RTC/NVRAM device for an M48T59/559 Timekeeper. It registers device `#r` with files `rtc` and `nvram`.

The device operations support attach, walk, stat, open, read, and write. `rtc` reads/writes seconds since epoch; writes parse a numeric time and convert to BCD RTC fields. `nvram` reads/writes byte ranges in the Timekeeper NVRAM and calls a placeholder checksum routine. Access is restricted: RTC writes require `eve`, and NVRAM requires `eve` plus `cpuserver`.

Hardware access uses address strobe ports `STB0/STB1` and `Data`, with `nvget`/`nvput`. `rtctime`, `setrtc`, `rtc2sec`, and `sec2rtc` handle BCD and Unix-time conversion. `watchreset` programs the watchdog to reset and spins.

Filesystem relevance is direct: this is a Plan 9 device filesystem node and participates in timekeeping, which affects file timestamps and system logs.

Notable risks: `nvcksum` is empty; RTC years are mapped 70-99 to 1970-1999 and below 70 to 2000-2069; direct NVRAM writes can alter firmware/platform state.

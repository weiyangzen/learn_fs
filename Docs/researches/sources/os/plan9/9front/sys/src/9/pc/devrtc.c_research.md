# File Research: sources/os/plan9/9front/sys/src/9/pc/devrtc.c

## Purpose
Plan 9 `#r` RTC/NVRAM device for PC CMOS real-time clock hardware at I/O ports `0x70/0x71`. It exposes kernel namespace files for wall-clock seconds and CMOS NVRAM.

## Exposed Interface
- Device table: `rtcdevtab`, device character `r`, name `rtc`.
- Files:
  - `rtc`: readable by all, writable only by `eve`; reads seconds since Unix epoch.
  - `nvram`: accessible only by `eve`; reads/writes 256 bytes of CMOS NVRAM starting at offset 128.
- Helper API exported to other kernel code:
  - `rtctime()`
  - `nvramread(int addr)`
  - `nvramwrite(int addr, uchar data)`

## Implementation Notes
- `rtcinit()` reserves the two CMOS I/O ports via `ioalloc`.
- `_rtctime()` polls RTC update-in-progress status, reads BCD seconds/minutes/hour/day/month/year, converts two-digit years to 1900/2000, then converts to epoch seconds.
- `rtctime()` serializes RTC/NVRAM access with `nvrtlock` and requires two identical successive reads to reduce rollover races.
- `rtcwrite()` accepts a decimal seconds value for `rtc`, converts it to BCD RTC fields, and writes CMOS clock registers.
- Time conversion is self-contained in `rtc2sec()`, `sec2rtc()`, and leap-year tables.

## Filesystem Relevance
This is a Plan 9 kernel device-file implementation: hardware is represented as files under a device namespace rather than as a block filesystem. It is relevant for understanding Plan 9 device/VFS conventions: `Chan`, `Dirtab`, `devwalk`, `devstat`, `devdirread`, `readnum`, and device permission checks.

## Risks / Quirks
- Uses 32-bit `ulong` seconds, so epoch range is limited.
- RTC year pivot assumes `<70` means 2000s and otherwise 1900s.
- NVRAM access is raw and privileged, with minimal validation beyond offset/size.

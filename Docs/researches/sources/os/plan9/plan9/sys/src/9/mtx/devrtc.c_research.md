# File Research: sources/os/plan9/plan9/sys/src/9/mtx/devrtc.c

## Role

MTX real-time clock and NVRAM device. It exposes `/dev/rtc` and `/dev/nvram`, supports BCD time conversion, checksum maintenance, and a watchdog reset hook.

This is time/NVRAM device support, not filesystem code.

## Main Interfaces

- Device operations:
  - `rtcattach`, `rtcwalk`, `rtcstat`, `rtcopen`, `rtcclose`
  - `rtcread`, `rtcwrite`, `rtcbwrite`
- NVRAM:
  - `nvput`
  - `nvget`
  - `nvcksum`
- Time:
  - `rtctime`
  - `setrtc`
  - `rtc2sec`
  - `sec2rtc`
- `watchreset`

## Data Structures

- RTC register constants and `Rtc` structure with second/minute/hour/day/month/year fields.
- `rtcdir[]` entries for `rtc` and `nvram`.

## Important Behavior

- Reads/writes RTC fields through CMOS-style address/data ports.
- Converts BCD encoded RTC fields to seconds since epoch and back.
- `rtcread` returns time as decimal seconds for `rtc` and raw bytes for `nvram`.
- `rtcwrite` accepts decimal time and updates RTC registers.
- `nvcksum` maintains checksum bytes over NVRAM contents.
- `watchreset` is a stub.

## Dependencies And Assumptions

- Uses port I/O helpers `inb`/`outb`.
- Assumes RTC/NVRAM layout compatible with the constants in this file.

## Notable Risks

- RTC century/year handling is manual and platform-specific.
- NVRAM checksum range assumptions must match firmware expectations.

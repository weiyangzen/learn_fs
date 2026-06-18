# File Research: sources/os/plan9/plan9/sys/src/9/pc/devrtc.c

Read completely: 461 lines.

This file implements the PC real-time clock and non-volatile RAM device `#r`.

Key behavior:
- Uses I/O ports `0x70` and `0x71`.
- Exposes `rtc` and `nvram`.
- `rtctime()` repeatedly reads CMOS BCD clock fields until two consecutive reads match.
- `rtcwrite()` accepts seconds since Unix epoch and writes BCD fields back to CMOS.
- `nvramread()` and `nvramwrite()` provide direct helpers for other kernel code.
- Device access restricts writes to `eve`.

Important interfaces:
- Device name: `rtc`, rune `'r'`.
- Files: `#r/rtc`, `#r/nvram`.
- Uses `readnum()` for textual RTC reads and direct byte copying for NVRAM.

Research notes:
- NVRAM user-visible space starts at CMOS offset `128` and has size `256`.
- Year conversion maps `00..69` to 2000-based years and `70..99` to 1900-based years.
- Calendar conversion functions implement leap-year handling.

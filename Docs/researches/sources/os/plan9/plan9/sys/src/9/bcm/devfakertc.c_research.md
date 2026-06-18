# File Research: sources/os/plan9/plan9/sys/src/9/bcm/devfakertc.c

Fake RTC device for Raspberry Pi systems without a hardware realtime clock.

Key behavior:
- Exposes `#r/rtc` through `fakertcdevtab`.
- Initializes `rtcsecs` from external `kerndate`.
- Registers `rtctick()` with `addclock0link()` to increment seconds every 1000 ms.
- `rtcread()` returns the current seconds value through `readnum()`.
- `rtcwrite()` accepts a positive numeric seconds value and updates the fake clock.

This provides enough RTC behavior for boot-time local clock setup via `#r/rtc`, but it is only a crude monotonic approximation from kernel build time unless userland writes a better value.

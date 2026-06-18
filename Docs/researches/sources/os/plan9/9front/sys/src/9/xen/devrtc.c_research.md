# File Research: sources/os/plan9/9front/sys/src/9/xen/devrtc.c

Xen wall-clock RTC device.

Purpose:
- Provides Plan 9 `#r/rtc` device backed by Xen wall-clock time.

Key behavior:
- Directory contains `.` and `rtc`.
- `rtcread` returns `xenwallclock()` as a numeric value.
- `rtcwrite` accepts writes to `rtc` but ignores contents and returns byte count.
- Standard Plan 9 device methods delegate attach/walk/stat/open to common helpers.

Integration:
- Supplies time-of-day access in the Xen kernel without hardware CMOS/RTC access.

Risks/notes:
- Writes do not change Xen wall-clock time.

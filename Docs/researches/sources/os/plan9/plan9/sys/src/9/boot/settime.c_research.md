# File Research: sources/os/plan9/plan9/sys/src/9/boot/settime.c

Boot-time clock setup.

Key behavior:
- `settime()` runs once.
- For local boot, tries `#r/rtc`; if unavailable, prompts user for `yymmddhhmm[ss]`.
- For non-local boot, temporarily mounts root on `/tmp` and uses root directory access time.
- Writes resulting epoch seconds to `#c/time`.
- `lusertime()` parses user date/time into seconds since Jan 1 1970 with leap-year handling.

This works with the fake RTC provided by `devfakertc.c` on BCM.

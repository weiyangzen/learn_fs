# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_time.c

Read completely: 239 lines.

This file provides kernel time helper routines that combine clock selection, remaining-time accounting, and conversion of absolute or relative timespecs into callout ticks.

Key functions:
- `tvhzto`, `tshzto`, and `tshztoup` compute ticks until an absolute wall/monotonic target by subtracting current time and calling `tvtohz`/`tstohz`.
- `inittimeleft` validates a relative timespec and snapshots monotonic uptime.
- `gettimeleft` subtracts elapsed monotonic time from a remaining timeout and returns the next tick count, or zero on timeout.
- `clock_timeleft` recomputes remaining time against a selected clock.
- `clock_gettime1` implements kernel clock selection for realtime, monotonic, process CPU time, and thread CPU time.
- `ts2timo` validates timespec input, converts absolute timers to relative timers, normalizes minimum values, rejects already-expired timers, and returns a positive tick count.

Integration: CPU clocks use `calcru`/`addrulwp` and process visibility authorization. Realtime and monotonic paths use the timecounter APIs. Arithmetic is delegated to `subr_time_arith.c`.

Reliability notes: process CPU clock lookup releases `proc_lock` before authorization against `p`; this reflects existing process lifetime conventions but is a sensitive area. `ts2timo` returns `ETIMEDOUT` for zero effective timeout rather than silently scheduling a zero tick delay.

# File Research: sources/os/bsd/openbsd-src/sys/kern/kern_tc.c

Read completely: 986 lines.

Implements the kernel timecounter framework and `timehands` fast timekeeping data. It provides boot/realtime/uptime/runtime accessors, timecounter registration and selection, realtime and monotonic clock stepping, NTP/adjtime/frequency adjustments, userland timekeep export, and `KERN_TIMECOUNTER` sysctls.

Core state:
- A dummy timecounter provides early boot time service until real hardware registers.
- Two `struct timehands` instances form a generation-stamped ring. Readers copy from `timehands` and retry if `th_generation` changes or is zero.
- `tc_lock` protects timecounter adjustments and explicit realtime changes; `windup_mtx` protects `tc_windup()` updates.
- `timecounter` points to the selected hardware counter; `tc_list` contains registered counters.
- `time_second`, `time_uptime`, and `naptime` are volatile cached values updated from `tc_windup()`.

Time read APIs:
- Boot-time accessors: `binboottime()`, `microboottime()`, `nanoboottime()`.
- Uptime accessors: `binuptime()`, `getbinuptime()`, `nanouptime()`, `microuptime()`, `getuptime()`, `nsecuptime()`, `getnsecuptime()`.
- Runtime excluding suspend/nap time: `binruntime()`, `nanoruntime()`, `getbinruntime()`, `getnsecruntime()`.
- Realtime accessors: `bintime()`, `nanotime()`, `microtime()`, `gettime()`, `getnanotime()`, `getmicrotime()`.
- Cached uptime conversions: `getnanouptime()` and `getmicrouptime()`.

Counter selection and updates:
- `tc_init()` computes precision, rejects counters needing too-frequent polling for current `hz`, inserts the counter, and auto-selects non-negative high-quality counters.
- `tc_reset_quality()` changes a counter's quality and falls back to the best remaining counter if the active counter degrades.
- `tc_getfrequency()` and `tc_getprecision()` report active counter properties.
- `inittimecounter()` sets the periodic windup tick interval and warms up the selected counter.
- `tc_ticktock()` periodically calls `tc_windup()` to prevent counter wrap and refresh cached time.

Clock setting and windup:
- `tc_setrealtimeclock()` steps UTC by recomputing boot time from requested realtime minus uptime, clears adjtime state, updates timehands, optionally logs the step, and mixes time into randomness.
- `tc_setclock()` steps the monotonic/realtime notion used after boot, advances `naptime` when needed, and calls `timeout_adjust_ticks()` so tick-based timeouts are not skipped after a forward jump.
- `tc_windup()` is the central update routine: copies current timehands, applies counter deltas, handles monotonic offset changes, boot-time changes, adjtime changes, NTP second processing, cached realtime conversion, counter switches, scale recalculation including frequency adjustment, generation publishing, timekeep export, and global cached seconds.
- `tc_update_timekeep()` publishes selected timekeeping fields to the shared `timekeep` area with producer memory barriers.

Adjustment and sysctl:
- `ntp_update_second()` consumes `th_adjtimedelta` in bounded per-second chunks and converts it into the counter scale adjustment.
- `tc_adjfreq()` gets or sets hardware counter frequency adjustment under `tc_lock`, forcing a windup on writes.
- `tc_adjtime()` gets or sets remaining adjtime delta using generation-stamped reads and windup writes.
- `sysctl_tc_hardware()` reads or switches the active timecounter by name.
- `sysctl_tc_choice()` returns available counters with qualities.
- `sysctl_tc()` exposes hardware, choice, tick interval, and timestep warning controls under `KERN_TIMECOUNTER`.

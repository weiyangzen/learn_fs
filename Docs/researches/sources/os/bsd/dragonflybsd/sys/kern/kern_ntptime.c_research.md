# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_ntptime.c

This file implements the kernel NTP PLL/FLL clock discipline interface, derived from David Mills' NTP kernel code and adapted to DragonFlyBSD timecounters. It provides `ntp_adjtime(2)` behavior, `kern.ntp_pll.gettime`, second-boundary adjustment calculations, leap-second state handling, and optional PPS synchronization support.

Core state:
- `time_state`, `time_status`, `time_tai`, `time_maxerror`, `time_esterror`, `time_reftime`, and `time_tick` track the externally visible NTP state.
- `time_offset`, `time_freq`, and `time_adj` are 64-bit fixed-point quantities for phase and frequency correction.
- `ntp_lock` serializes sysctl and syscall updates.
- Under `PPS_SYNC`, `pps_tf[]`, `pps_freq`, jitter/stability counters, watchdog state, and averaging interval controls maintain PPS discipline state.

Important functions:
- `ntp_sysctl()` snapshots current nanosecond time and NTP state into `struct ntptimeval`, then reports `TIME_ERROR` when unsynchronized, clock-error, or PPS fault conditions apply.
- `sys_ntp_adjtime()` copies in `struct timex`, checks `SYSCAP_NOSETTIME` when modification modes are requested, updates selected kernel clock variables, calls `hardupdate()` for phase input, clamps frequency to `MAXFREQ`, and copies the resulting state back to userland.
- `ntp_update_second()` runs at second rollover on CPU 0. It advances leap-second state, computes the next one-second nanosecond adjustment from `time_offset` and `time_freq`, decays the remaining offset, and handles PPS watchdog expiry.
- `ntp_init()` initializes `time_tick`, clears phase/frequency variables, and initializes PPS fields at boot.
- `hardupdate()` updates PLL/FLL phase and frequency estimates when `STA_PLL` is enabled, using `time_uptime - time_reftime` to decide PLL vs FLL contribution and clamping final frequency.
- `hardpps()` is compiled only with `PPS_SYNC`; it range-gates PPS samples, median-filters phase, tracks jitter, calibrates frequency over adaptive intervals, and can update `time_freq`.

Concurrency and privileges:
- `sys_ntp_adjtime()` holds `ntp_lock` and enters a critical section while mutating time discipline fields.
- Modification requires capability privilege `SYSCAP_NOSETTIME`; read-only state retrieval does not.
- The code expects second-update integration with the clock subsystem and assumes `ntp_update_second()` is called on CPU 0.

Filesystem/storage relevance:
- Not filesystem-specific, but accurate time affects file timestamps, vnode metadata, cache coherency decisions, and time-based storage tests.

Notable risk/quirk:
- The NTP code preserves historical kernel discipline semantics and contains comments warning that old comments may not fully match DragonFly's timecounter integration.

# File Research: sources/os/bsd/netbsd-src/sys/kern/kern_ntptime.c

## Purpose
Implements kernel NTP time discipline and `adjtime(2)` second-by-second slewing, with optional PPS synchronization and sysctl/syscall reporting.

## Main Interfaces
- `ntp_gettime`: returns current time, max/estimated error, TAI offset, and state.
- `sys_ntp_adjtime`, `ntp_adjtime1`: process user NTP adjustments, authorization, state update, and result copyout.
- `ntp_update_second`: updates leap-second state and computes next per-second adjustment from NTP PLL/FLL and `adjtime`.
- `ntp_init`: initializes fixed-point adjustment state.
- `hardupdate`: updates local PLL/FLL phase/frequency estimates.
- `hardpps`: optional PPS signal discipline when `PPS_SYNC` is enabled.
- `ntp_timestatus`, `sys___ntp_gettime50`, `sysctl_kern_ntptime`.

## Internal State And Dependencies
- Uses 64-bit fixed-point `l_fp` macros for time/frequency values.
- NTP globals include `time_state`, `time_status`, `time_tai`, `time_maxerror`, `time_esterror`, `time_reftime`, `time_offset`, `time_freq`, and `time_adj`.
- `time_adjtime` tracks `adjtime(2)` correction in microseconds.
- Protected by `timecounter_lock` spin mutex for state access.
- Depends on syscalls, kauth time authorization, timecounter `nanotime`, sysctl, and optional `PPS_SYNC`.

## Control Flow Notes
- `ntp_adjtime1` applies mode bits for status, max/est error, time constant, TAI, frequency, offset, precision mode, clock source, and PPS maximum interval.
- `ntp_update_second` advances leap-second state, computes NTP offset/frequency adjustment, expires PPS signal validity, and layers `adjtime` slewing at 5000 ppm or 500 ppm depending on remaining correction.
- `hardupdate` clamps phase offset and applies PLL/FLL frequency correction depending on elapsed time and mode bits.
- `hardpps` filters PPS samples with range/frequency checks, median phase filtering, jitter/wander counters, adaptive averaging interval, and optional frequency update.

## Risk Areas
- Many variables exist only under `NTP`/`PPS_SYNC`; callers must respect feature guards.
- All core routines assert or assume `timecounter_lock` at clock priority.
- Frequency and phase clamping prevent runaway values; changing constants affects clock discipline stability.
- Leap-second handling mutates `newsec` and `time_tai`.

## Filesystem Relevance
Indirect. Timekeeping affects file timestamps and sync timing but this file is not VFS-specific.

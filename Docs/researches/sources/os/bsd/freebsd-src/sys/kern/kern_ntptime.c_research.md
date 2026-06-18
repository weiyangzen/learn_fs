# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_ntptime.c

Read completely: 1049 lines.

## Purpose
Implements FreeBSD's kernel NTP clock discipline interface, including `ntp_gettime(2)`, `ntp_adjtime(2)`, `adjtime(2)`, PLL/FLL state updates, optional PPS synchronization, leap-second state handling, per-second tick adjustments, and periodic RTC save scheduling.

## Main Elements
- Maintains NTP state variables: `time_state`, `time_status`, TAI offset, max/estimated error, PLL time offset, frequency offset, tick adjustment, and pending `adjtime` slew.
- Uses 64-bit fixed-point helpers for time and frequency arithmetic.
- `ntp_is_time_error()` maps status bits to trusted/untrusted time state.
- `ntp_gettime1()`, `sys_ntp_gettime()`, and `ntp_sysctl()` report current nanosecond time, errors, TAI, and state.
- `kern_ntp_adjtime()` validates privilege, applies mode-controlled changes to status, errors, time constant, TAI, PPS parameters, frequency, and offset, then returns updated `timex` state.
- `sys_ntp_adjtime()` is the copyin/copyout syscall wrapper.
- `ntp_update_second()` advances error accounting, processes leap insert/delete state transitions, computes next-second adjustment from PLL/FLL and `adjtime`, and returns TAI offset.
- `hardupdate()` updates phase/frequency estimates from daemon-provided offsets, selecting PLL or FLL behavior based on interval and status.
- Optional `hardpps()` processes PPS events with range checks, median filtering, jitter/wander accounting, frequency calibration, interval adjustment, and PPS-driven clock discipline.
- `kern_adjtime()` and `sys_adjtime()` implement microsecond-level clock slewing.
- Periodic `resettodr` callout writes synchronized time to the RTC and also runs during shutdown pre-sync.

## Dependencies And Integration
Uses spin mutex `ntp_lock`, sysctl, privilege checks (`PRIV_NTP_ADJTIME`, `PRIV_ADJTIME`), timecounter interfaces, PPS/timepps support, eventhandlers, callouts, `resettodr()`, and syscall copyin/copyout.

## Risk Notes
All NTP state is protected by a spin mutex, except a few documented lockless status reads for RTC save decisions. Privileged callers can set broad clock discipline state. PPS logic rejects noisy or malformed samples but depends on precise timecounter captures. Leap-second handling mutates `newsec` and TAI offset inside the per-second update path.

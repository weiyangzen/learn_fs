# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_lockstat.c

## Purpose
Defines FreeBSD lockstat SDT probes and a timestamp helper used by lock instrumentation.

## Key Interfaces
- SDT provider: `lockstat`.
- Probe groups cover adaptive mutexes, spin mutexes, rwlocks, sx locks, lockmgr locks, and thread spinning.
- `lockstat_nsecs()` returns a nanosecond timestamp for profiling when lockstat is enabled.

## State And Locking
The only mutable state is `volatile bool __read_frequently lockstat_enabled`. No local locks are used.

## Control Flow
`lockstat_nsecs()` returns zero if lockstat is disabled or the lock object has `LO_NOPROFILE`. Otherwise it calls `binuptime()` and converts `bintime` to nanoseconds.

## Integration Notes
Probe names match kernel locking subsystems, for example `lockmgr__block`, `rw__upgrade`, and `sx__downgrade`. Other lock implementations record against these probes via lockstat macros.

## Risks
The timestamp conversion is intentionally lightweight but approximate to nanoseconds from `bintime`. Callers must treat zero as disabled/no-profile rather than an actual timestamp.

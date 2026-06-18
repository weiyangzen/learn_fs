# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_counter.c

## Purpose
Implements MI wrappers and sysctl handlers for per-CPU 64-bit counters, plus an MP-friendly rate-check helper built on counters.

## Main Elements
- Counter allocation and access:
  - `counter_u64_alloc()`, `counter_u64_free()`, `counter_u64_zero()`, `counter_u64_fetch()`.
  - Uses `pcpu_zone_8` per-CPU UMA storage.
- Sysctl handlers:
  - `sysctl_handle_counter_u64()` exports a single counter and zeros it on any write attempt.
  - `sysctl_handle_counter_u64_array()` exports an array of counters and zeros all counters on write.
- Rate limiting:
  - `struct counter_rate`: event counter, reset lock, last tick, over-limit state, and period.
  - `counter_rate_alloc()` / `counter_rate_free()`.
  - `counter_rate_get()` returns current count or zero if the period has expired.
  - `counter_ratecheck()` increments the counter and returns 0, -1, or the previous over-limit count depending on rate state.
- Sysinit helpers:
  - `counter_u64_sysinit()` and `counter_u64_sysuninit()` allocate/free counters referenced by static initializers.

## Dependencies And Integration
Depends on per-CPU UMA zones, `<sys/counter.h>` inline primitives, kernel ticks/hz, atomics, sysctl, and malloc type `M_COUNTER_RATE`.

## Risk Notes
`counter_ratecheck()` intentionally avoids a heavyweight lock but can skip updates when another thread is resetting the counter. The code uses both `ticks` and `tick` names in rate age checks, so correctness depends on the intended kernel globals/macros. Sysctl writes have destructive semantics: any write zeros the exported counter or array.

# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_cpufreq.c

## Summary
Implements the generic CPU frequency backend registry, state validation, latency measurement, suspend/resume preservation, and cross-call based get/set operations.

## Main Responsibilities
- Initializes a singleton `struct cpufreq` backend protected by `cpufreq_lock`.
- Registers one backend after boot, validating callbacks and frequency states.
- Filters state entries to descending, valid values and measures transition latency.
- Sets all CPUs to the maximum registered frequency on registration.
- Provides backend/state/frequency query APIs and per-CPU/all-CPU setters.
- Saves minimum-frequency suspend transition and restores prior frequency on resume.

## Important Behavior
`cpufreq_register()` refuses registration while `cold`, rejects duplicate backends, drops invalid/duplicate/out-of-order states, and deregisters on validation or latency failure. All hardware callback invocations are made via `xc_unicast()` or `xc_broadcast()` and waited synchronously.

`cpufreq_get_state_raw()` performs a binary search over descending frequencies and returns the nearest state selected by the search even if the input frequency is not an exact state.

## Dependencies
Uses `sys/cpufreq.h` backend callbacks, `xcall`, `nanotime()`, `timespecsub()`, `kmem`, and a global mutex.

## Risks
Only one backend is supported. Latency sampling divides total successful time by the fixed sample count even if slow samples were skipped, so reported latency is a suitability heuristic, not a precise average.

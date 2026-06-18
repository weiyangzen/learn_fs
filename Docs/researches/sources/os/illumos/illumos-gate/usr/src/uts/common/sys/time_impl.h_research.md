# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/time_impl.h

## Purpose
Implementation-level time definitions shared by kernel and user headers, centered on POSIX `timespec`, `itimerspec`, clock IDs, and timer flags.

## Main Interfaces
- Defines `time_t` when not already provided.
- Defines `struct timespec`, `timestruc_t`, and `struct itimerspec`.
- Provides 32-bit conversion and overflow macros for `timespec` and `itimerspec`.
- Defines `timestruc` as an SVr4 alias for `timespec`.
- Defines clock IDs: `CLOCK_REALTIME`, `CLOCK_MONOTONIC`, `CLOCK_THREAD_CPUTIME_ID`, `CLOCK_PROCESS_CPUTIME_ID`, `CLOCK_VIRTUAL`, plus alternate names `CLOCK_HIGHRES` and `CLOCK_PROF`.
- Defines `CLOCK_MAX`, `TIMER_RELTIME`, and `TIMER_ABSTIME`.

## Dependencies And Relationships
Includes `sys/feature_tests.h` and, outside assembly, `sys/types32.h`. It is included by `sys/time.h` and timer-related headers that need stable clock/timer structure definitions without all of `sys/time.h`.

## Research Notes
This file owns the ABI-visible clock constants and 32-bit structure shims, so changes here affect libc, kernel timer code, and compatibility layers.

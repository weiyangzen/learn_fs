# File Research: sources/os/bsd/freebsd-src/sys/sys/boottrace.h

## Purpose
`boottrace.h` defines lightweight boot, run, and shutdown trace interfaces for kernel and userland.

## Main Interfaces
- Sysctl names: `kern.boottrace.boottrace`, `kern.boottrace.runtrace`, and `kern.boottrace.shuttrace`.
- Message format is bounded by thread-name and event-name lengths.
- Userland macros format a message and call `sysctlbyname()`.
- Kernel macros guard trace emission on `boottrace_enabled`.
- Kernel functions include `boottrace`, reset, resize, and console dump.

## Implementation Notes
Userland `_boottrace()` truncates through `vsnprintf()` but still submits any nonnegative formatted result. Kernel `BOOTTRACE_INIT` supplies `"kernel"` as the thread/actor name.

## Dependencies and Constraints
Userland depends on stdarg/stdio/string/sysctl headers. Kernel trace calls are no-ops when disabled and are controlled by global booleans.

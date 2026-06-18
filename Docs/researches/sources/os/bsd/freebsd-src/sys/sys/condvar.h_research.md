# File Research: sources/os/bsd/freebsd-src/sys/sys/condvar.h

## Purpose
Defines FreeBSD kernel condition variables and their wait/signal API.

## Main Elements
- `struct cv` stores a wait-channel description and waiter count.
- Lifecycle: `cv_init()` and `cv_destroy()`.
- Wait variants: regular, unlock-on-wait, signal-interruptible, timed, and timed signal-interruptible.
- Public macros adapt lock objects from mutex/rw-style lock structs to internal `_cv_*` functions.
- Wake APIs: `cv_signal()` and `cv_broadcastpri()`; `cv_broadcast()` maps to priority 0.

## Dependencies And Integration
Kernel-only APIs operate on `struct lock_object`; timed waits use `sbintime_t`, `tick_sbt`, and callout flags.

## Risk Notes
The waiter count is protected by the caller’s associated condition mutex. Correct usage requires holding the same lock across predicate checks, waits, and signal/broadcast operations.

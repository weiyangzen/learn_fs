# File Research: sources/os/bsd/freebsd-src/sys/sys/selinfo.h

Kernel readiness notification state for `select(2)`, `poll(2)`, and kqueue-style consumers.

Key responsibilities:
- Defines `struct selinfo`, holding sleeping selector threads, a `knlist`, and a mutex pointer.
- Provides `SEL_WAITING(si)` to test whether selector threads are queued.
- Declares kernel routines `selrecord()`, `selwakeup()`, `selwakeuppri()`, `seldrain()`, and `seltdfini()`.

Important patterns:
- `si_tdlist` tracks threads sleeping for readiness on an object.
- `si_note` integrates the same object with kqueue notifications.
- The object embedding `selinfo` supplies or references the lock used to protect selector state.

Research relevance:
- Small but central bridge between file/socket/device readiness and user-visible multiplexing APIs.

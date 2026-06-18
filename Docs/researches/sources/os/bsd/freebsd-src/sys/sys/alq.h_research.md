# File Research: sources/os/bsd/freebsd-src/sys/sys/alq.h

Kernel asynchronous logging queue API.

Key elements:
- Kernel-only header defining opaque `struct alq`, global logging daemon thread pointer, and `struct ale`.
- Defines flags for wait behavior, activation, and ordered writes.
- Declares queue open, write, flush, close, get/post APIs.
- Provides inline `alq_post()` wrapper.

Dependencies:
- Kernel-only; uses `struct thread` and `struct ucred`.

Research notes:
- ALQ writes queued log entries to files asynchronously.
- Useful for low-overhead tracing/accounting paths that must avoid synchronous disk writes in hot code.

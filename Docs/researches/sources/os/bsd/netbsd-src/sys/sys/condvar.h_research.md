# File Research: sources/os/bsd/netbsd-src/sys/sys/condvar.h

Declares NetBSD kernel condition variable type and operations.

Key content:
- `kcondvar_t` is an opaque two-pointer structure.
- Kernel APIs: `cv_init`, `cv_destroy`, wait variants, timed wait variants, signal, broadcast.
- Timed APIs support tick-based and `bintime` timeout forms, with interruptible `_sig` variants.
- Introspection helpers: `cv_has_waiters`, `cv_is_valid`.
- Global `lbolt`, awakened once per second by the clock interrupt.

Important behavior:
- Declarations are only exposed to `_KERNEL`.
- Wait APIs pair with `struct kmutex`.

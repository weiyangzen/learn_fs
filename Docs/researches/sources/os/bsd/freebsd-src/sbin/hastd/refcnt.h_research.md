# File Research: sources/os/bsd/freebsd-src/sbin/hastd/refcnt.h

`refcnt.h` defines a lightweight atomic reference counter type and inline operations for HAST. `refcnt_t` is an unsigned int; initialization is a direct store, acquire uses `atomic_add_acq_int()`, and release uses `atomic_fetchadd_int(count, -1)`.

`refcnt_release()` returns the decremented value and asserts the old count was nonzero. A comment notes an unresolved question about whether release should include a release memory barrier.

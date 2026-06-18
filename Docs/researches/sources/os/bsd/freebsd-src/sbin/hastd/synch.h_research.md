# File Research: sources/os/bsd/freebsd-src/sbin/hastd/synch.h

`synch.h` wraps pthread mutexes, rwlocks, and condition variables in assertion-checked inline helpers for HAST. The wrappers include Clang thread-safety annotations such as `__locks_exclusive`, `__unlocks`, and `__requires_exclusive`.

Mutex and rwlock wrappers assert successful init/destroy/lock/unlock operations, `mtx_trylock()` accepts only success or `EBUSY`, and `mtx_owned()` uses FreeBSD's `pthread_mutex_isowned_np()`. Condition variables are initialized with `CLOCK_MONOTONIC`; `cv_timedwait()` treats timeout zero as an indefinite wait and otherwise returns whether `ETIMEDOUT` occurred.

# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/condvar_impl.h

This private condition-variable implementation header defines `condvar_impl_t` with a waiter count and `CV_HAS_WAITERS`.

It also defines `cvwaitlock_t`, a reader/writer-style lock built from a mutex and condition variable, allowing recursive reader entry while a writer may be waiting. Macros initialize/destroy it, enter/exit read or write mode, and downgrade write to read. The comments explicitly note possible writer starvation and no priority inheritance.

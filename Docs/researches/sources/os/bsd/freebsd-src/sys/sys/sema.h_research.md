# File Research: sources/os/bsd/freebsd-src/sys/sys/sema.h

Kernel counting semaphore interface.

Key responsibilities:
- Defines `struct sema` as a mutex, condition variable, waiter count, and semaphore value.
- Declares initialization, destruction, post, wait, timed wait, trywait, and value query functions.
- Wraps internal calls with `LOCK_FILE` and `LOCK_LINE` metadata for lock diagnostics.

Important patterns:
- This is a sleepable synchronization primitive implemented with a mutex and condition variable.
- Public macros preserve simple call sites while passing source location to the underlying implementation.
- Exposed only as a kernel synchronization API, not a userspace semaphore ABI.

Research relevance:
- Useful for kernel subsystems that need bounded resource admission or producer/consumer waits without hand-rolling condition-variable state.

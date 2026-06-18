# File Research: sources/os/bsd/dragonflybsd/sys/sys/condvar.h

Kernel condition-variable interface.

Key responsibilities:
- Defines `struct cv` with a spinlock, waiter count, and description string.
- Declares init/destroy, wait, timed wait, signal/broadcast, and waiter-test functions.
- Provides wrappers for waits against either `struct lock` or `struct mtx`.
- Provides signal-interruptible and timeout variants through macros around internal functions.

Dependencies:
- Includes `sys/spinlock.h` and `sys/mutex.h`; forward-declares `struct lock`.

Notable risks:
- Wait macros depend on caller holding the matching lock type expected by the internal implementation.
- `cv_broadcastpri` ignores priority and aliases to broadcast.

# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_spin.c

This file implements public POSIX spinlocks. `pthread_spin_init` validates `pshared`, sets the spinlock magic, stores the flag, and initializes the underlying `pthread_spin_t` through internal lock initialization. The comment notes process-shared is not otherwise used because CPU simple locks have the desired properties here.

Destroy validates magic and returns `EBUSY` if the simple lock is not unlocked, then marks the object dead. Lock repeatedly calls the internal trylock and `pthread__smt_wait` until successful. Trylock maps failure to `EBUSY`; unlock releases via cached lock ops and calls `pthread__smt_wake`.

Integration points: depends on `pthread_lock.c` lock primitives and private magic values. Risks are CPU-burning behavior under contention, lack of ownership checking on unlock, and process-shared semantics being accepted but not explicitly coordinated beyond simple-lock behavior.

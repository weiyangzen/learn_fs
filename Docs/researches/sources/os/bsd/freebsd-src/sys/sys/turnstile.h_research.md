# File Research: sources/os/bsd/freebsd-src/sys/sys/turnstile.h

Kernel turnstile priority-propagation wait queue interface for contested non-sleepable locks.

Key responsibilities:
- Documents the turnstile lifecycle: chain locking, wait/trywait/cancel, lookup, signal/broadcast, unpend, disown, claim, allocation, and free.
- Defines exclusive and shared queue identifiers.
- Declares initialization, priority adjustment, allocation/free, broadcast/signal, chain lock/unlock, claim/disown, empty/head lookup, turnstile lookup/trywait/wait/unpend, lock/unlock, and assertion APIs.

Dependencies:
- Kernel-only; forward-declares `lock_object`, `thread`, and `turnstile`.

Notable risks:
- Correct use requires pairing high-level lock state changes with turnstile ownership and `turnstile_unpend()` wakeups.
- Priority inheritance correctness depends on accurate owner claiming when a lock with waiters is acquired.

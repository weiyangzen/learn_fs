# File Research: sources/os/bsd/netbsd-src/sys/sys/sleepq.h

Read completely: 94 lines.

This kernel synchronization header declares generic sleep queue operations. It exposes `sleepq_t` and APIs for init, remove, enter, enqueue, transfer, uncatch, unsleep, timeout, wake, abort, priority change/lending, and blocking.

Kernel code also gets `sleepqlock_t`, a cache-line-sized lock wrapper, and `sleepq_dontsleep`, which prevents sleep during cold startup or shutdown/panic/idle conditions. It includes `sleeptab.h` for hash table and turnstile definitions.

Risks: sleep queue operations coordinate LWP state, wait channels, locks, timeouts, and signal interruptibility. Callers must pass the right interlocks and sync object metadata.

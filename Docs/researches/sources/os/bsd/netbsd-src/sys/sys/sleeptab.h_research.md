# File Research: sources/os/bsd/netbsd-src/sys/sys/sleeptab.h

Read completely: 140 lines.

This header defines the hashed sleep table and turnstile structures. The sleep table has 128 queues selected by `SLEEPTAB_HASH(wchan)`, and kernel inline helpers acquire the corresponding spin lock while returning the queue or lock.

It also defines `turnstile_t`, specialized sleep queues for kernel locks, with reader/writer queues, waiter counts, priority inheritance state, and hash-chain/free-list links. Kernel APIs include turnstile init, lookup, constructor, exit, block, wakeup, print, unsleep, priority change, and pool globals.

Risks: wait-channel hashing shifts pointer values and maps many wait objects onto shared locks. Turnstiles carry priority inheritance state, so queue and inheritor updates must be serialized.

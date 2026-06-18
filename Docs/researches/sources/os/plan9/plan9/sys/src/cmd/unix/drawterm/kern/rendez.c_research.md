# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/rendez.c

This file implements Plan 9-style sleep/wakeup on `Rendez` wait queues.

Key behavior:
- `sleep` evaluates a predicate under the rendezvous lock, queues `up` if false, unlocks, and blocks through `procsleep`.
- `wakeup` removes one process from the rendezvous wait queue and wakes it.

Important details:
- The predicate is rechecked before queuing, matching the standard Plan 9 sleep protocol.
- Processes are linked through `Proc.rnext`.
- `sleep.c` contains a duplicate implementation in this tree.

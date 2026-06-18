# File Research: sources/os/plan9/9front/sys/src/9/port/qlock.c

Blocking `QLock` and reader/writer lock implementation.

Key responsibilities:
- Implements interruptible `eqlock()` and non-interruptible `qlock()`.
- Implements nonblocking `canqlock()` and `qunlock()`.
- Implements `rlock()`, `runlock()`, `wlock()`, `wunlock()`, and `canrlock()` for `RWLock`.
- Queues waiting processes using `Proc.qnext`, process states `Queueing`, `QueueingR`, and `QueueingW`.
- Records caller PCs for lock diagnostics.

Important behavior:
- `eqlock()` can be interrupted by pending notes before or during wait; interrupted waiters are pulled by `procinterrupt()`.
- Unlocking a `QLock` hands ownership directly to the next queued process by preserving `locked` and setting owner PC.
- `RWLock` prefers queued writers: readers only enter immediately if no writer and no queued process.
- `wunlock()` wakes one writer or all consecutive queued readers.

Notable risks:
- Calling these while holding ilocks or normal locks prints diagnostics because sleeping while holding locks is unsafe.

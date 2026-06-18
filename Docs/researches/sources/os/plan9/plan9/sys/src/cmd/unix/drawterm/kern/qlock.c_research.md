# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/qlock.c

This file implements sleepable queued locks for hosted drawterm kernel code.

Key behavior:
- `qlock` acquires a `QLock`, queues the current process if busy, and sleeps it.
- `canqlock` attempts a non-blocking acquire.
- `qunlock` releases the lock or wakes the next queued process.
- `holdqlock` reports whether the current process owns the lock.
- Private `queue`/`dequeue` maintain FIFO `Proc` wait lists.

Important details:
- Waiting processes are marked `Queueing` and resumed with `procwakeup`.
- Ownership is tracked in `q->owner`, allowing `holdqlock` checks.

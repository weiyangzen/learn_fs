# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/rwlock.c

This file implements a simple reader-writer lock by layering counters on `QLock`.

Key behavior:
- `rlock` serializes against `x` and increments reader count.
- `runlock` decrements reader count and releases writer exclusion when the last reader exits.
- `wlock` takes writer exclusion.
- `wunlock` releases writer exclusion.

Important details:
- The implementation favors simplicity over advanced fairness.
- The `QLock` fields inside `RWlock` provide sleeping behavior.

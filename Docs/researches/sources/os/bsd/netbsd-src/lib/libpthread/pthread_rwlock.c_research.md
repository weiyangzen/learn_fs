# File Research: sources/os/bsd/netbsd-src/lib/libpthread/pthread_rwlock.c

This file implements pthread read/write locks and attributes. The lock owner field packs state flags and either a writer thread pointer or reader count. Reader acquisition increments the owner count when no writer or waiting writer is present; writer acquisition CASes from no owner to `self | RW_WRITE_LOCKED`. Both paths prefer writers once `RW_WRITE_WANTED` is set.

Contended readers and writers use a hash interlock mutex and `PTQ` sleep queues. Writers are queued tail-first; readers are inserted at the head of the reader queue. Unlock releases reader or writer ownership and, when waiters exist and the lock becomes unowned, directly hands off to the first waiting writer or all waiting readers. Handoff marks target threads' `pt_rwlocked` state and unparks them through helper functions. Timed waits use `pthread__park`; `pthread__rwlock_early` repairs queue and waiter bits if a timed waiter wakes before handoff.

Try-locks return `EBUSY` without sleeping, timed lock calls validate absolute timeout fields, and NetBSD `_np` helpers inspect held/read/write-held state. Attribute support is minimal; process-shared code appears guarded and unsupported.

Risks are complex flag packing, direct handoff correctness, writer preference fairness tradeoffs, and guarded `_PTHREAD_PSHARED` code referencing `ptr` instead of `attr`, which would matter if compiled.

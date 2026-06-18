# File Research: sources/os/bsd/dragonflybsd/sys/kern/sysv_sem.c

## Summary
Implements SVID/System V semaphores, including semaphore-set creation, control operations, atomic multi-operation `semop`, process-exit undo records, and SysV IPC tunables.

## Main Responsibilities
- Initializes the semaphore ID pool and per-set locks in `seminit()`.
- Maintains global semaphore totals under `sema_lk`.
- Allocates and manages per-process `sem_undo` records for `SEM_UNDO`.
- Clears undo entries when semaphore sets or members are reset or removed.
- Implements `sys___semctl()` for `IPC_RMID`, `IPC_SET`, `IPC_STAT`, `SEM_STAT`, `GET*`, `SETVAL`, and `SETALL`.
- Implements `sys_semget()` for keyed lookup and semaphore-set creation.
- Implements `sys_semop()` with atomic vector execution, rollback, wait counts, sleeps, wakeups, and undo adjustment.
- Implements `semexit()` to apply process-exit undo adjustments and clean up undo structures.

## Important Behavior
Each semaphore set has a lock; individual semaphore operations also use pool tokens based on the semaphore address. `sys_semop()` first tries to apply the whole operation vector. If one operation cannot proceed, it increments the appropriate wait counter (`semncnt` or `semzcnt`), rolls back all earlier changes, optionally sleeps, then retries from the beginning. This preserves atomic visibility of the vector.

`SEM_UNDO` adjustments are applied after a successful operation vector. If undo allocation fails partway through, the code rolls back earlier undo adjustments and then rolls back semaphore value changes. `semexit()` later applies stored adjustments while revalidating set and entry state under locks.

Semaphore IDs use index-plus-sequence encoding. Set removal clears `SEM_ALLOC`, frees the semaphore array, decrements `semtot`, and removes matching undo entries.

## Dependencies and Integration
This file depends on `ipcperm()`, process credentials and tokens, jail SysV IPC capability checks, per-process `p_sem_undo`, lockmgr locks, pool tokens, sysctl/tunables, and sleep/wakeup.

## Risks
Correctness depends on rollback paths for both semaphore values and undo records. The wait path must handle destroy/recreate races, so it tracks a per-set generation counter. `semexit()` includes race-aware rechecks but still asserts if it finds impossible stale allocation state outside expected races.

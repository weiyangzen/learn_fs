# File Research: sources/os/bsd/freebsd-src/sys/kern/sysv_sem.c

## Purpose
Implements FreeBSD System V semaphore support as the `sysvsem` kernel module, including `semget`, `semop`, `__semctl`, semaphore undo-on-exit state, sysctl export, RACCT accounting, MAC checks, jail scoping, and legacy/32-bit ABI compatibility.

## Main Structures and State
- `struct sem`: per-semaphore value, last-operation PID, wait-for-increase count, and wait-for-zero count.
- `struct sem_undo`: per-process SEM_UNDO adjustment vector, stored in active/free lists.
- Global pools: `sema` for semaphore identifiers, `sem` for contiguous semaphore objects, `semu` for undo records, `sema_mtx[]` for per-set locking.
- Global locks: `sem_mtx` protects allocation/removal and pool compaction; `sem_undo_mtx` protects undo lists.
- `seminfo` exposes tunables and limits such as `semmni`, `semmns`, `semopm`, `semume`, `semvmx`, and `semaem`.

## Core Behavior
- `seminit()` allocates pools, initializes locks/MAC labels, sets up jail OSD state, registers process-exit hooks, and installs syscalls.
- `sys_semget()` finds a keyed semaphore set in the caller prison or allocates a new set, enforces limits, initializes `ipc_perm`, records credentials, and consumes RACCT `RACCT_NSEM`.
- `kern_semctl()` handles `IPC_RMID`, `IPC_SET`, `IPC_STAT`, `SEM_STAT`, `GET*`, `SETVAL`, and `SETALL`, applying permission checks, MAC checks, copyin/copyout safety, undo clearing, and waiter wakeups.
- `kern_semop()` validates operation vectors, computes required permissions, executes operations atomically with rollback on blocking/error, supports timed waits, manages `SEM_UNDO`, and updates `sempid`/`sem_otime`.
- `semexit_myhook()` applies outstanding SEM_UNDO adjustments at process exit and returns undo records to the free list.
- `sem_remove()` clears permissions, drops RACCT/credential references, clears undo entries, wakes waiters, and compacts the contiguous semaphore pool while locking affected sets.

## Jail and Visibility Model
- `sem_find_prison()` maps caller credentials to the jail root controlling System V semaphore visibility.
- `sem_prison_cansee()` only permits access to semaphore sets owned by the root prison or its descendants.
- `sem_prison_check/set/get/remove/cleanup()` implement `sysvsem` jail parameter semantics, including disable/new/inherit modes and cleanup of semaphores owned by a removed prison.

## External Interfaces
- Syscalls: `__semctl`, `semget`, `semop`, and old `semsys` where enabled.
- Sysctls under `kern.ipc.*`: semaphore limits plus opaque `sema` export.
- `kern_get_sema()` provides sanitized kernel copies for consumers that need semaphore metadata.
- Compatibility blocks translate old `semid_ds` layouts and FreeBSD32 pointer/structure formats.

## Dependencies
Uses kernel IPC permission helpers, audit hooks, RACCT, MAC framework, jail OSD, eventhandler process-exit hooks, syscall helper registration, mutexes, and sysctl.

## Notes and Risks
- Removal compacts the global semaphore array, so pointer updates and locking around `__sem_base` are critical.
- `GETALL`/`SETALL` intentionally drop and reacquire the set mutex around allocation/copyin, relying on sequence validation to detect replacement.
- Undo accounting is bounded by `seminfo.semume` and `seminfo.semmnu`; overflow returns `EINVAL`/`ENOSPC` and rolls back semaphore changes.

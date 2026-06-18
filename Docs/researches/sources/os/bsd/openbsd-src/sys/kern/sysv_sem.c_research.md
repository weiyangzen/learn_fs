# File Research: sources/os/bsd/openbsd-src/sys/kern/sysv_sem.c

Implements System V semaphore sets, semaphore operations, undo records, process-exit cleanup, and sysctl tunables.

Global state:
- `sema`: array mapping semaphore indexes to `struct semid_ds_kern`.
- `semseqs`: per-index sequence numbers for id generation.
- `semu_list`: global list of per-process undo vectors.
- `sema_pool`, `semu_pool`: pools for semaphore sets and undo structures.
- `semtot`, `semutot`: allocated semaphore and undo accounting.

Initialization and allocation:
- `seminit()` initializes pools, allocates `sema` and `semseqs`, and initializes the undo list.
- `sys_semget()` preallocates new sets when creation may be needed, handles key lookup and races, enforces `semmni`, `semmns`, and `semmsl`, initializes permissions, sequence, timestamps, and semaphore arrays.

Control operations:
- `sys___semctl()` handles `IPC_RMID`, `IPC_SET`, `IPC_STAT`, `GETNCNT`, `GETPID`, `GETVAL`, `GETALL`, `GETZCNT`, `SETVAL`, and `SETALL`.
- Removal clears the `sema` slot, drops references, clears undo records for that set, and wakes waiters.
- `SETVAL`/`SETALL` clear affected undo entries and wake waiters.
- `GETALL` and `SETALL` use references around sleeping allocations/copyin and retry if the set is replaced.

Semaphore operation semantics:
- `sys_semop()` copies small operation vectors onto the stack and larger vectors from heap allocation.
- It applies a vector atomically: if any operation cannot proceed, prior changes are rolled back before sleeping or returning.
- Negative operations wait for sufficient value, zero operations wait for zero, and positive operations increment values.
- `IPC_NOWAIT` returns `EAGAIN` instead of sleeping.
- Waiters increment `semncnt` or `semzcnt`, sleep on the semaphore slot, then revalidate that the set still exists.
- Successful operations update `sempid`, `sem_otime`, and wake other waiters when needed.

Undo handling:
- `semu_alloc()` allocates one undo vector per process, with a second lookup after sleeping allocation to avoid duplicates.
- `semundo_adjust()` creates, updates, or removes per-process undo entries and enforces `SEMUME`.
- `semundo_clear()` removes undo entries for an entire set or individual semaphore.
- `semexit()` applies pending undo adjustments when a process exits, clamps underflow to zero, wakes waiters, and frees the undo vector.

Sysctl behavior:
- `sysctl_sysvsem()` exposes bounded tunables and can grow `semmni` dynamically via `sema_reallocate()`.
- Some limits are read-only or only growable to avoid invalidating active state.

Filesystem/storage relevance:
- Not filesystem logic. Relevant as a kernel resource manager with id/sequence validation, permission checks, sleep-safe allocation, reference counting, and process-exit cleanup patterns.

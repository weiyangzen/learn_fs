# File Research: sources/os/bsd/netbsd-src/sys/kern/sysv_shm.c

## Purpose

`sysv_shm.c` implements NetBSD's System V shared memory facility: segment creation, lookup, attach/detach, control operations, fork/exit integration with VM spaces, memory wiring, and sysctl-tunable limits.

## Main Responsibilities

- Maintains global shared-memory segment descriptors and per-segment wait condition variables.
- Implements `shmget`, `shmat`, `shmdt`, and `shmctl`.
- Tracks per-vmspace shared-memory mappings through `vm_shm`.
- Integrates with UVM by installing `uvm_shmfork` and `uvm_shmexit` callbacks.
- Supports `SHM_LOCK`, `SHM_UNLOCK`, `_SHM_RMLINGER`, and global physical-memory locking policy.
- Exposes `shmmax`, `shmmni`, `shmseg`, `shmmaxpgs`, and `shm_use_phys` sysctls.

## Core Data Model

`shmsegs` is the global array of `struct shmid_ds` descriptors. Each allocated segment owns a UVM anonymous object in `_shm_internal`. `shm_nused` and `shm_committed` enforce descriptor and total-page limits.

Each vmspace's `vm_shm` points to a `shmmap_state`, which contains a refcounted list of mappings. Fork shares the mapping list and increments segment attach counts; detach or mutation uses `shmmap_getprivate()` to split a shared map.

## Segment Lifecycle

`shmget()` finds existing segments by key or allocates a new descriptor. During UAO allocation it marks the descriptor allocated but removed, increments `shm_realloc_disable`, drops the global lock, then finalizes permissions and wakes any key lookup waiters.

`shmat()` validates ID, sequence, permissions, attach count, address alignment, and flags, then inserts a mapping entry, references the UVM object, and maps it with shared inheritance.

`shmdt()` removes the per-vmspace mapping, decrements attach count, unmaps the address range, and frees the segment if it had been removed and the last attachment is gone.

`shmctl1()` supports `IPC_STAT`, `IPC_SET`, `IPC_RMID`, `SHM_LOCK`, and `SHM_UNLOCK`. Removal is deferred until `shm_nattch` reaches zero unless there are no attachments.

## Concurrency Notes

`shm_lock` protects descriptors, mapping lists, counters, and reallocation state. `shm_realloc_state`, `shm_realloc_disable`, and `shm_realloc_cv` prevent descriptor-array resizing while an allocation has dropped the lock. Per-segment condition variables wake waiters for in-progress keyed creation.

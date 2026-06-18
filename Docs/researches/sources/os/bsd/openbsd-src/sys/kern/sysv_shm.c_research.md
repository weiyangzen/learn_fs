# File Research: sources/os/bsd/openbsd-src/sys/kern/sysv_shm.c

Implements System V shared memory segments backed by UVM anonymous objects.

Global state and structures:
- `shmsegs`: array mapping shmid indexes to `struct shmid_ds`.
- `shmseqs`: per-index sequence numbers.
- `shm_pool`: pool for `struct shmid_ds` plus an internal `struct shm_handle`.
- `shm_last_free`, `shm_nused`, `shm_committed`: allocation cursor and accounting.
- Per-vmspace `struct shmmap_head` tracks attached shared-memory mappings.
- `struct shm_handle` stores the backing `uvm_object`.

Lookup and allocation:
- `shm_find_segment_by_key()` and `shm_find_segment_by_shmid()` locate segments by key or id/sequence.
- `sys_shmget()` handles existing-key lookup, `IPC_CREAT`, `IPC_EXCL`, and new segment allocation.
- `shmget_allocate_segment()` enforces size, count, and total committed-page limits; allocates a pool object; creates a UAO object; initializes permissions, sequence, pid, timestamps, and size.
- Allocation retries when a keyed segment appears while sleeping.

Attach/detach:
- `sys_shmat()` lazily allocates per-vmspace mapping state, validates permissions, finds a free attachment slot, computes fixed or chosen attach address, references the backing UAO, maps it with `MAP_INHERIT_SHARE`, and records the attachment.
- `sys_shmdt()` finds an attachment by virtual address and delegates to `shm_delete_mapping()`.
- `shm_delete_mapping()` decrements attachment count, unmaps the range, records detach time, and deallocates removed segments once the final attach is gone.

Control and lifecycle:
- `sys_shmctl()` implements `IPC_STAT`, `IPC_SET`, and `IPC_RMID`; lock/unlock commands are unsupported.
- `IPC_RMID` marks a segment removed and either deallocates immediately or waits for the last detach.
- `shmfork()` copies attachment state and increments segment attach counts in child vmspaces.
- `shmexit()` detaches all mappings and frees the per-vmspace attachment table.
- `shminit()` initializes the pool and arrays and converts `shmmax` from pages to bytes.

Sysctl behavior:
- `sysctl_sysvshm()` exposes bounded shared-memory tunables.
- `shmmni` can grow dynamically via `shm_reallocate()`.
- `shmall` and other constraints are handled conservatively so existing allocations remain valid.

Filesystem/storage relevance:
- Not filesystem code, but storage-relevant through virtual memory object backing, shared mappings inherited across fork, and lifecycle patterns similar to file-backed mmap objects.

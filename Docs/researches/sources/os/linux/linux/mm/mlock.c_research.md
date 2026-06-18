# File Research: sources/os/linux/linux/mm/mlock.c

## Role

`mlock.c` implements memory locking and unlocking: `mlock(2)`, `mlock2(2)`, `munlock(2)`, `mlockall(2)`, `munlockall(2)`, folio-level mlock/munlock helpers, and System V shared-memory lock accounting. Its job is to keep selected user pages unevictable while respecting resource limits and capability checks.

## Main Responsibilities

- Enforce `RLIMIT_MEMLOCK` and `CAP_IPC_LOCK`.
- Maintain `VM_LOCKED` and `VM_LOCKONFAULT` VMA flags.
- Walk existing mappings to mark or unmark resident folios.
- Move folios between evictable and unevictable LRU state with approximate `mlock_count` tracking.
- Batch LRU operations per CPU to reduce lock churn.
- Account locked pages in `mm->locked_vm`, `NR_MLOCK`, unevictable VM events, and user shared-memory ucounts.

## Key Entry Points

- `can_do_mlock()`: shared permission check.
- `mlock_folio()`: mark an existing LRU folio mlocked and enqueue it for unevictable handling.
- `mlock_new_folio()`: mark a newly allocated folio mlocked before it enters LRU.
- `munlock_folio()`: enqueue folio unlock processing.
- `mlock_drain_local()`, `mlock_drain_remote()`, `need_mlock_drain()`: drain per-CPU mlock batches.
- `SYSCALL_DEFINE2(mlock, ...)`, `SYSCALL_DEFINE3(mlock2, ...)`, `SYSCALL_DEFINE2(munlock, ...)`: range locking syscalls.
- `SYSCALL_DEFINE1(mlockall, ...)`, `SYSCALL_DEFINE0(munlockall)`: process-wide locking syscalls.
- `user_shm_lock()` and `user_shm_unlock()`: shared-memory lock accounting against `ucounts`.

## Folio Batch Design

`struct mlock_fbatch` stores a per-CPU `folio_batch` protected by a local lock. Low pointer bits distinguish three queued operations: mlock an existing LRU folio, mlock a new non-LRU folio, or munlock. `mlock_folio_batch()` decodes each entry, relocks the appropriate lruvec, performs LRU state changes, unlocks once at the end, and drops folio references.

This batching is important because mlock state can be updated from fault, migration, and syscall paths while avoiding excessive LRU lock traffic.

## LRU and Unevictable Logic

`__mlock_folio()` clears the LRU bit, relocks the folio’s lruvec, and moves non-evictable folios to unevictable state. If the folio is already unevictable and still mlocked, it increments `mlock_count`. `__munlock_folio()` decrements `mlock_count`, clears `PG_mlocked` when appropriate, updates `NR_MLOCK`, and rescues folios back to evictable LRU when `folio_evictable()` becomes true.

The code intentionally treats `mlock_count` as approximate in some races; reclaim can correct stranded unevictable folios.

## VMA Flag Transitions

`apply_vma_lock_flags()` iterates a target address range, verifies contiguous VMA coverage, computes new lock flags, and calls `mlock_fixup()` for each VMA segment. `mlock_fixup()` filters unsupported VMAs, performs VMA split/merge flag modifications, updates `mm->locked_vm`, and calls `mlock_vma_pages_range()` unless the range was already locked.

`mlock_vma_pages_range()` temporarily combines `VM_LOCKED` with `VM_IO` in the new flags to signal rmap walkers and avoid double-counting during concurrent migration/reclaim interactions, then walks PTEs with `PGWALK_WRLOCK_VERIFY`.

## Syscall Semantics

`do_mlock()` aligns the range, checks permissions, adjusts for already locked pages when testing limits, applies VMA flags under `mmap_write_lock`, then populates pages with `__mm_populate()` unless `MLOCK_ONFAULT` deferred locking was requested. `mlockall()` updates `mm->def_flags` for future mappings and optionally applies flags to current VMAs; `munlockall()` clears process-wide lock flags.

## Special Cases

Secretmem VMAs cannot be unlocked through this path. Zone-device pages and huge zero PMDs are skipped by the page walker. Large folios are only mlocked when the mapped range fully covers the folio; munlock is allowed on partially mapped large folios so later reclaim/splitting can recover pages no longer protected by `VM_LOCKED`.

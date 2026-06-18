# File Research: sources/os/linux/linux/mm/mmap_lock.c

Mmap-lock tracing and VMA-lock support. This file supplies tracepoint wrappers, per-VMA lock exclusion mechanics, RCU VMA lookup/locking fast paths, and careful mmap-lock acquisition for page-fault handling.

Key responsibilities:
- Exports mmap-lock tracepoints and tracing helper functions when tracing is enabled.
- Implements per-VMA reader exclusion under `CONFIG_PER_VMA_LOCK` using VMA refcounts, lock sequence numbers, `rcuwait`, and lockdep annotations.
- Provides `lock_vma_under_rcu()` for stable RCU lookup plus per-VMA read locking without taking `mmap_lock`.
- Provides `lock_next_vma()` for RCU-safe VMA iteration with fallback to mmap read locking when speculation fails.
- Implements `lock_mm_and_find_vma()` for page-fault paths under `CONFIG_LOCK_MM_AND_FIND_VMA`, including careful kernel-fault exception-table checks and stack expansion.
- Provides a no-MMU fallback that simply takes `mmap_read_lock()` and looks up the VMA.

Important behavior:
- `__vma_start_write()` excludes VMA readers, records the mm lock sequence into `vma->vm_lock_seq`, then ends exclusion so later readers see the VMA as write-locked relative to the mm sequence.
- Detaching a VMA uses a special exclusion target so the writer waits until no readers remain and then leaves the VMA detached.
- `vma_start_read()` may return false locked results, but must never return a false unlocked result; it uses refcount acquisition and sequence checks to reject VMAs under write.
- If a VMA is detached during RCU lookup, the RCU walker can retry from the address instead of trusting stale iterator state.
- `lock_next_vma()` speculates on mmap-lock sequence state to verify gaps; if uncertain, it reacquires under mmap read lock and restarts the iterator.
- Fault-time `lock_mm_and_find_vma()` avoids deadlock on kernel faults by only blocking on the mmap lock when the faulting instruction is exception-table-covered.

Dependencies:
- VMA refcount fields, `mm_lock_seq`, maple/VMA iterators, mmap rwsem helpers, RCU, rcuwait, lockdep, exception tables, stack expansion helpers, and VM event counters.

Notable risks:
- Per-VMA locking depends on subtle refcount states and sequence-number ordering; false positives are acceptable only when they force fallback, not when they allow unsafe access.
- RCU iterator state must be reset after fallback locking or detach races.
- Kernel page faults must not blindly block on mmap locks unless exception-table metadata proves the fault is recoverable.

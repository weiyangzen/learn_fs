# sources/test-tools/stress-ng/stress-tlb-shootdown.c

## Purpose
Implements the `tlb-shootdown` stressor, a multi-process memory workload that repeatedly changes page protections, reads and writes shared mappings, calls `madvise()`/`msync()`, and rotates CPU affinity to force TLB shootdowns and IPIs.

## Important APIs, Types, And Functions
`stress_tlb_shootdown_read_mem()` and `stress_tlb_shootdown_write_mem()` read or write every cache line in selected pages, with writes followed by cache flushes. `stress_tlb_shootdown_mmap()` retries shared mapping allocation. `stress_tlb_shootdown_child()` is the worker process loop that alternates `mprotect()` states, whole-mapping reads/writes with a prime-derived stride, optional `MADV_DONTNEED` on anonymous and file-backed pages, and periodic CPU affinity changes. `stress_tlb_shootdown()` sets up shared mappings, forks workers, coordinates start, runs parent-side page invalidation, records interrupt counters, and cleans up.

## Control Flow
The stressor obtains eligible CPUs, maps shared PID synchronization slots, optionally creates an unlinked temporary file for a small shared file-backed mapping, and maps a 512-page shared anonymous region. It chooses between two and eight child processes based on CPU count, initializes per-child sync state, then forks children. Children apply scheduler settings, mark themselves OOM-killable, wait for release, pin to CPUs, and repeatedly mprotect/read/write/advice both shared regions. The parent waits at the global barrier, releases child sync, and loops issuing optional `MADV_DONTNEED`, synchronous `msync()`, Linux debugfs TLB flush ceiling read/write, and hugepage collapse/nohugepage advice. On termination it records TLB and IPI deltas, emits metrics, kills and reaps children, unmaps memory, removes temp storage, unmaps PID sync state, and frees CPU arrays.

## State And Persistence Behavior
Runtime state is shared anonymous memory, optional unlinked file-backed memory, child processes, temporary directory, and affinity state. The optional debugfs read/write targets `/sys/kernel/debug/x86/tlb_single_page_flush_ceiling` by writing back the same content, so it should not intentionally change the value. Temp files are unlinked and directories removed.

## Dependencies And Integration Points
The implemented path requires `sched_getaffinity` and `mprotect`. Optional blocks use `madvise`, `MADV_DONTNEED`, `MADV_COLLAPSE`, `MADV_NOHUGEPAGE`, file-backed mmap, and Linux debugfs. It uses stress-ng affinity, interrupts, sync-pid, temp-file, kill/wait, prime, cache, and memory usage helpers. It registers as `CLASS_TLB | CLASS_MEMORY` with `VERIFY_NONE`.

## Risks And Test Signals
The workload intentionally races permission changes and memory accesses across processes, so kernel and architecture behavior can vary. Debugfs may be absent or permission restricted and is ignored. Child fork failures reduce worker count rather than aborting. Test signals include positive TLB shootdowns/sec and IPIs/sec metrics, bogo progress in parent and children, clean child reap, and no leaked temp directory or mappings.

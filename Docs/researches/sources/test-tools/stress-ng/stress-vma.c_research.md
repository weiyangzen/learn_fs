# sources/test-tools/stress-ng/stress-vma.c

## Purpose
Implements `vma`, a multi-process, multi-pthread stressor for kernel virtual-memory-area structures. It races mmap, munmap, mlock, madvise, mincore, mprotect, msync, `/proc` map reads, memory accesses, and optional pagemap scanning.

## Important APIs, types, and functions
`stress_vma()` is the entry point when pthread support exists. `stress_vma_context_t` carries args and candidate address; `stress_thread_info_t` maps functions to thread counts; `stress_vma_metrics_t` stores shared racy counters. `stress_mmapaddr_get_addr()` probes for an unmapped 32-page range. Worker functions cover VMA syscalls plus signal counters for `SIGSEGV` and `SIGBUS`.

## Control flow
The stressor maps shared metrics, synchronizes, and runs an OOM-managed child. That child starts `STRESS_VMA_PROCS` subprocesses. Each subprocess repeatedly finds an address, forks a child, starts a configured mix of pthreads for about 10 seconds, cancels them, and is killed/reaped by the parent side. Supervising code mirrors mmap count into bogo operations.

## State and persistence
Shared anonymous metrics and a shared page are the main state. `stress_vma_continue_flag` coordinates loops. Metrics are deliberately racy. No persistent files are written; `/proc/self/maps` and `/proc/self/pagemap` are read only.

## Dependencies and integration points
Registered as `stress_vma_info` with `CLASS_VM` and `max_metrics_items = STRESS_VMA_MAX`. Depends on pthreads, fork synchronization, OOM child handling, signal handlers, mmap helpers, kill helpers, scheduler settings, optional `PR_SET_VMA_ANON_NAME`, and optional Linux `PAGEMAP_SCAN`.

## Risks and edge cases
Benign `SIGSEGV` and `SIGBUS` are expected because mappings are unstable. `MAP_FIXED` probing must avoid text/heap regions. Syscall failures are normal under races and mostly ignored. Thread cancellation during VM syscalls can leave partial metric updates, contained by process boundaries.

## Test signals
Metrics report rates for mmaps, munmaps, locks, protects, accesses, `/proc` reads, signals, and optional pagemap scans. Resource skips occur for missing shared mappings or no pthread support.

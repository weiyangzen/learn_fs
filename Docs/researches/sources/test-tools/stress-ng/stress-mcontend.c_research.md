# sources/test-tools/stress-ng/stress-mcontend.c

Purpose: implements `mcontend`, a memory-contention stressor that pounds two mappings of the same backing page from multiple threads, using explicit barriers, cache flushes, optional x86 fences, and optional NUMA placement.

Important APIs/types/functions: `page_write_sync()` prepares a one-page backing file. `read64()` and `read64_lfence()` issue volatile reads with memory barriers and optional x86 `lfence`. `stress_memory_contend()` performs repeated writes, barriers, reads, `mfence`, cache-line flushes, and x86 `pause` sequences. `stress_memory_contend_thread()` loops this work in helper pthreads and may change CPU affinity. `stress_mcontend()` sets up mappings, NUMA, locks memory, starts threads, and drives the main loop.

Control flow: the stressor creates a temp backing file, writes one page, maps it twice privately, optionally randomizes NUMA placement, mlocks both mappings, synchronizes, starts four helper threads, and runs contention locally while helpers do the same. On each main iteration it may `msync()` mappings and increments bogo ops.

State and persistence: global state includes blocked-signal set and optional CPU list. The backing file is unlinked and temp directory removed. Mappings are unmapped and CPU lists freed on exit.

Dependencies/integration: requires pthread support. Optional dependencies include sched affinity, Linux mempolicy, x86 assembly helpers, cache flush helpers, mmap, mlock, and temp-file helpers.

Risks/test signals: intentionally creates heavy cache-line bouncing and memory-order pressure. Useful signals are unimplemented without pthreads, successful two-mapping setup, helper thread joins, temp cleanup, and bogo progress under contention.

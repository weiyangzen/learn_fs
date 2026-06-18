# sources/test-tools/stress-ng/stress-llc-affinity.c

Purpose: implements `llc-affinity`, a last-level-cache stressor that repeatedly changes CPU affinity while reading and writing an LLC-sized memory buffer, optionally flushing cache lines, locking memory, and randomizing NUMA placement.

Important APIs/types/functions: `cache_line_func_t` abstracts read/write loops. Specialized write functions cover 64-byte and arbitrary cache-line sizes, with optional x86 `clflush`/`clflushopt` and PPC `dcbst`. `stress_llc_affinity()` orchestrates CPU list discovery, cache-size selection, NUMA setup, function selection, affinity changes, memory traffic, and metrics.

Control flow: the stressor obtains allowed CPUs, catches SIGILL for optional assembly opcodes, reads options, discovers LLC size and line size if not specified, scales size by NUMA node count, mmaps a buffer at least as large as CPU count times page size or LLC size, optionally randomizes NUMA pages and `mlock`s memory, selects read/write functions, sync-starts, and loops setting affinity to the next CPU, reading the buffer, writing the buffer, and incrementing bogo ops.

State and persistence behavior: anonymous memory buffer, optional NUMA masks, CPU affinity mask, and metrics are process-local. CPU affinity is changed repeatedly and not explicitly restored before process exit.

Dependencies and integration points: requires `sched_setaffinity`. Integrates with stress-ng affinity, CPU cache discovery, NUMA, mmap, signal, target-clone, and architecture assembly helpers. Registered as `CLASS_CPU_CACHE`.

Risks: cache-size discovery can fail; assembly cache flush instructions may be unavailable despite compile support, hence SIGILL catch. NUMA page randomization and mlock can require resources. Static `val` counters inside target-cloned functions are not synchronized across workers, which is acceptable for stress but not correctness data.

Test signals: run with explicit and discovered sizes, clflush enabled/disabled, NUMA enabled where supported, mlock under limits, and many CPUs. Confirm metrics for read MB/s, write MB/s, and affinity changes/sec.

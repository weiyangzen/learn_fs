# sources/test-tools/stress-ng/core-shared-cache.c

Purpose: allocates shared memory buffers sized to CPU data cache characteristics so stressors can coordinate cache- and cacheline-oriented workloads.

Important APIs/types/functions: `stress_shared_cache_alloc` determines and maps `g_shared->mem_cache.buffer` and `g_shared->cacheline.buffer`. `stress_shared_cache_free` unmaps them.

Control flow: allocation first normalizes NUMA node count and exits early to mapping if `g_shared->mem_cache.size` was already configured. It queries CPU cache details; on failure it defaults to `2 MiB * numa_nodes`. It clamps requested cache level to the detected maximum, finds a data cache at that level, and either sizes by selected cache ways or full cache size multiplied by NUMA nodes. It logs cache sizes, maps anonymous shared memory for the cache buffer and a separate per-process cacheline buffer, names mappings, and reports errors on mmap failure.

State and persistence: mutates fields under global `g_shared`. Shared anonymous mappings persist until explicit free or process exit.

Dependencies/integration: depends on CPU cache discovery, NUMA helpers, mmap naming/unmapping, `g_shared` layout, and warning/logging helpers. Stressors read these shared buffers for memory/cache activity.

Risks: if cache buffer mapping succeeds but cacheline mapping fails, the first mapping is not immediately unwound in the error path. Cache detection can be incomplete on unusual CPUs, causing default sizing. `stress_warn_once` suppresses repeated diagnostics.

Test signals: no-cache-info fallback, cache-level clamp, cache-way clamp, multi-NUMA sizing, mmap failure injection, and free after partial allocation.

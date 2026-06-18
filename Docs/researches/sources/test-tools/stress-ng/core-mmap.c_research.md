# sources/test-tools/stress-ng/core-mmap.c

Purpose: implements mmap utility routines used by stress-ng memory stressors: page-fill/check patterns, anonymous shared mappings, forced unmapping, Linux pagemap statistics, page population, and deliberate physical-page fragmentation.

Important APIs/functions: `stress_mmap_set`, `stress_mmap_check`, `stress_mmap_set_light`, `stress_mmap_check_light`, `stress_mmap_populate`, `stress_mmap_anon_shared`, `stress_munmap_force`, `stress_mmap_stats`, `stress_mmap_stats_sum`, `stress_mmap_stats_report`, `stress_mmap_populate_forward`, `stress_mmap_populate_reverse`, and `stress_mmap_discontiguous`. The x86 `rep stosq` fast path is compiled when detected and not ILP32.

Control flow: fill/check helpers iterate page-by-page while honoring `stress_continue_flag()`. `stress_mmap_populate` first tries `MAP_POPULATE`, then falls back to ordinary `mmap`, manually touching anonymous pages. `stress_munmap_force` retries `munmap` on low-memory failures and handles huge-page length mismatches by consulting `/proc/<pid>/smaps`. `stress_mmap_stats` scans `/proc/self/pagemap` one page at a time and derives present, swapped, dirty, exclusive, null, unknown, and physically contiguous counts.

State/persistence: no durable state; it mutates mapped memory, `errno`, and stress-ng metrics. Kernel state is observed through procfs and changed through mmap, munmap, mprotect, madvise, and optional SysV shared memory on Fiwix.

Dependencies/integration: depends on `stress-ng.h`, CPU/cache helpers, `core-mmap.h`, `core-put.h`, random MWC generation, memory-page-size helpers, metrics, Linux procfs, and platform feature macros.

Risks: assumes buffer alignment and sizes suitable for 64-bit/page stepping; pagemap access can be permission restricted; huge-page detection is Linux-specific; manual population can fault or SIGBUS if used on unsuitable file mappings; `STRESS_MMAP_REPORT_FLAGS_UKNOWN` preserves a misspelled public flag name.

Test signals: mmap stressors with write-check/page-in paths, huge-page unmap cases, Linux/non-Linux builds, restricted `/proc/self/pagemap`, short/read-only mappings, and metric emission for all report flags.

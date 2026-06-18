# sources/test-tools/stress-ng/stress-memfd.c

Purpose: implements `memfd`, an OS/memory stressor for `memfd_create()`, file growth, mappings, fallocate holes, lseek modes, close-range cleanup, optional NUMA placement, mlock, madvise, and a zap-PTE regression check.

Important APIs/types/functions: `flags[]` cycles memfd flag combinations. `stress_memfd_fill_pages_generic()` writes patterned 64-bit values at cache-line stride. `stress_memfd_check()` validates those patterns for the zap-PTE test. `stress_memfd_child()` contains the workload and runs under `stress_oomable_child()` via `stress_memfd()`.

Control flow: the child reads options, scales `memfd-bytes`, allocates fd/map arrays, optionally prepares NUMA masks, builds unusual names, synchronizes, then repeatedly creates many memfds, truncates and maps them, optionally mlocks/NUMA-randomizes/madvises, fills pages, punches holes and fallocates, exercises `lseek()` modes, unmaps, optionally performs zap-PTE two-page truncate/pageout verification, closes fd ranges, tests invalid names/flags, cycles a valid flag combination, records timing, and increments bogo ops.

State and persistence: memfds are anonymous file descriptors and are closed every iteration. Arrays and NUMA masks are freed at exit. Metrics report nanoseconds per successful `memfd_create`.

Dependencies/integration: gated by `HAVE_MEMFD_CREATE`; optional dependencies include Linux memfd flags, madvise `MADV_PAGEOUT`, NUMA, mlock, close_range, fallocate, OOM wrapper, and SIGILL catch.

Risks/test signals: high fd counts can hit `EMFILE`/`ENFILE`; large mappings can trigger OOM. Useful signals are resource handling, `VERIFY_ALWAYS`, no zap-PTE data mismatch, successful fd cleanup, and memfd-create timing metrics.

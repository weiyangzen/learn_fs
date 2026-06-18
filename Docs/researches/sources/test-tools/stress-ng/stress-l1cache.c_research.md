# sources/test-tools/stress-ng/stress-l1cache.c

Purpose: implements `l1cache`, a CPU L1 data-cache thrashing stressor that computes or discovers cache geometry, allocates an aligned buffer, and repeatedly reads/writes addresses chosen to evict L1 sets.

Important APIs/types/functions: `stress_l1cache_info_ok()` fills missing cache parameters from user options or Linux cache discovery. `stress_l1cache_info_check()` validates `size == ways * sets * line_size`. Method functions implement forward, reverse, and random access patterns, each with verification variants. `stress_l1cache_methods[]` maps option names to functions.

Control flow: the stressor reads `--l1cache-*` settings, selects a method and verification function, validates geometry, mmaps four times the cache size, optionally `mlock`s it, aligns a pointer by set size, reports memory, sync-starts, and loops invoking the method. Each method runs many read/write passes across twice the cache size and updates a static set index; verification variants read back expected byte values. The main loop adds `l1cache_sets` bogo ops per pass and unmaps on exit.

State and persistence behavior: only anonymous memory and static per-method set counters persist during the process. No filesystem state is written.

Dependencies and integration points: uses stress-ng CPU-cache discovery, mmap, madvise, memory usage, settings, and metrics helpers. Registered as `CLASS_CPU_CACHE`, verification optional.

Risks: incorrect cache geometry can cause ineffective stress or out-of-range alignment. Reverse loops use pointer comparisons that depend on careful unsigned address behavior. Verification may fail if the access pattern writes overlapping random locations in ways not expected by the deterministic seed reset.

Test signals: run with auto-detected geometry and explicit size/sets/ways/line-size combinations, all three methods, `--verify`, and `--l1cache-mlock`. Confirm invalid geometry fails cleanly and memory is unmapped.

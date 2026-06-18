# sources/test-tools/stress-ng/core-thrash.c

## Purpose
`core-thrash.c` implements the optional background memory-thrashing helper used to perturb system memory, page cache, NUMA placement, KSM, slab reclaim, and process page residency while other stressors run.

## Important APIs, Types, And Functions
The public API is `stress_thrash_start` and `stress_thrash_stop` with no-op stubs when unavailable. Internals include signal handlers `stress_thrash_handler` and `stress_thrash_pagein_handler`, `/proc/<pid>/maps` parsing via `stress_thrash_read_proc_maps`, page-in routines `stress_thrash_pagein_self`, `stress_pagein_proc`, and `stress_thrash_pagein_all_procs`, sysfs/proc writers such as `stress_thrash_compact_memory`, `stress_thrash_zone_reclaim`, `stress_thrash_kmemleak_scan`, `stress_thrash_slab_shrink`, `stress_thrash_drop_caches`, and `stress_thrash_merge_memory`, plus NUMA/mapping perturbation helpers such as `stress_thrash_move_pages` and `stress_thrash_fragment_mappings`.

## Control Flow
On supported Linux builds, `stress_thrash_start` forks a helper, records parent/child PIDs, installs signal handlers, may raise scheduling priority, and loops while `thrash_run` and the parent are alive. The loop reads kernel memory knobs, walks process maps, pages in readable mappings, tries NUMA page migration where available, fragments mappings, and triggers reclaim/compaction/KSM-style operations. `stress_thrash_stop` signals and waits for the helper.

## State And Persistence
Runtime state includes `thrash_pid`, `parent_pid`, `thrash_run`, and signal jump buffers. The helper reads `/proc` and `/sys`, and may write to kernel control files such as compaction, drop-caches, KSM, slab shrink, kmemleak, and zone reclaim controls depending on permissions. It does not persist project files, but it deliberately changes kernel VM behavior during a run.

## Dependencies And Integration Points
It depends on Linux `/proc`, `/sys`, signal handling, `core-mmap`, `core-numa`, `core-killpid`, scheduler APIs, and stress-ng global continue flags. It is enabled by stressors/options that request memory thrashing, for example coverage-script cases using `--thrash`.

## Risks
This is intentionally intrusive. Kernel knobs may require privileges, may be absent, or may have system-wide effects. Parsing `/proc/<pid>/maps` is format-sensitive. Signal/longjmp cleanup must avoid leaving helpers running. NUMA and move-pages paths are highly platform- and privilege-dependent.

## Test Signals
Runtime coverage comes from memory stressors invoked with `--thrash` in `kernel-coverage.sh`, plus manual runs on Linux with and without NUMA and privileged sysfs access. Expected non-support should degrade to skipped or no-op behavior rather than failure.

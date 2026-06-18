# sources/test-tools/stress-ng/stress-mmapmany.c

Purpose: implements `mmapmany`, a VM stressor that creates as many small mappings as allowed, punches a hole in the middle page of each mapping, traverses proc map files, verifies surviving pages, and tears everything down.

Important APIs/types/functions: `stress_mmapmany_child()` is the OOM-wrapped worker. It uses `sysconf(_SC_MAPPED_FILES)` capped by `MMAP_MAX`, optional `mmapmany-mlock`, optional `mmapmany-numa`, and Linux-only `stress_mmapmany_read_proc_file()` to read `/proc/self/smaps` and `/proc/self/maps`.

Control flow: the child allocates a pointer table, optionally allocates NUMA masks, reports memory usage, synchronizes, then repeatedly maps three pages at a time. It optionally NUMA-randomizes and mlocks the mapping, writes two page-separated patterns, unmaps the middle page, and records the mapping. After the mapping phase it reads proc map files, verifies the first and third pages still contain the expected values, and force-unmaps all three page positions.

State and persistence: only the heap mapping table and optional NUMA masks persist within the process. No filesystem state is created. All mappings are anonymous and are cleaned at the end of each iteration.

Dependencies and integration: uses core mmap, NUMA, out-of-memory wrapper, memory usage reporting, bogo counters, and optional Linux proc interfaces.

Risks and test signals: the stressor can exhaust VMA counts, locked-memory limits, or memory. Verification catches accidental corruption of pages adjacent to an unmapped hole. Expected signals are resource skips under OOM, successful proc traversal, bogo increments per middle-page unmap, and no stale mappings after cleanup.

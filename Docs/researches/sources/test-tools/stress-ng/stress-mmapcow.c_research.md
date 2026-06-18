# sources/test-tools/stress-ng/stress-mmapcow.c

Purpose: `stress-mmapcow.c` stresses copy-on-write and page unmapping behavior. It maps shared anonymous buffers of increasing size, dirties pages to force faults/COW-like costs, unmaps pages in multiple patterns, optionally forks to increase copying pressure, and can apply `MADV_FREE`, mlock-on-fault, and NUMA placement.

Important APIs/types/functions: option flags `MMAPCOW_FORK`, `MMAPCOW_FREE`, `MMAPCOW_MLOCK`, and `MMAPCOW_NUMA` control behavior. `stress_mmapcow_force_unmap` tries `MADV_DONTNEED`/`MADV_FREE` before unmapping the whole buffer after page unmap failures. `stress_mmapcow_modify_unmap` times the first write/page fault, fills a page, flushes cache data, optionally advises free, and unmaps the page. `stress_mmapcow_exercise` selects one of eight access/unmap patterns. `stress_mmapcow_child` loops and records metrics.

Control flow: `stress_mmapcow` reads options, enables only supported flags, allocates NUMA masks when requested, synchronizes, and runs the oomable child. The child starts with one page, calls `stress_mmapcow_exercise`, doubles buffer size after success, backs off after failed sizes, and reports nanoseconds per page modification plus max mmap size. Exercise patterns include forward, even/odd forward, prime stride, reverse, reverse even/odd, random mincore-checked pages, one random populated page then full unmap, and random mergeable/unmergeable advice with sequential unmap. Optional fork runs the same mapping in a child and waits for it.

State and persistence behavior: state is anonymous memory and optional global NUMA masks. No filesystem state is created. Buffer sizing state (`buf_size`, `failed_size`, `failed_count`, `max_buf_size`) persists only in the child loop.

Dependencies and integration points: the stressor depends on `madvise`, mmap, CPU cache flush helpers, NUMA, OOM, prime stride helpers, and metrics. It registers as `CLASS_VM | CLASS_OS` with `VERIFY_NONE`; without madvise it registers unimplemented.

Risks: partial page unmaps can fail under memory pressure because VMA splitting may allocate memory; the force-unmap path is essential. Fork mode multiplies pressure and must avoid running children during low memory. Reverse pointer loops over unsigned-like addresses require careful termination conditions. `VERIFY_NONE` means data correctness is not asserted, only syscall resilience and metrics.

Test signals: run `stress-ng --mmapcow 1 --mmapcow-ops 1`, then options `--mmapcow-free`, `--mmapcow-fork`, `--mmapcow-mlock`, and `--mmapcow-numa` on capable hosts. Debug output should show max mmap size, and no child processes or mappings should remain.

# sources/test-tools/stress-ng/stress-physmmap.c

Purpose: `stress-physmmap.c` implements the Linux `physmmap` stressor, attempting to mmap physical System RAM ranges from `/dev/mem` page by page and optionally read from successful mappings.

Important APIs/types/functions: `stress_physmmap_t` represents a `/proc/iomem` System RAM range, with base address, size, page count, bitmap of still-mappable pages, mappable flag, and list link. `stress_physmmap_supported()` requires `CAP_SYS_ADMIN`. `stress_physmmap_get_ranges()` parses `/proc/iomem`; `stress_physmmap_flags()` randomizes `MAP_SHARED`/`MAP_PRIVATE` and optional `MAP_POPULATE`; `stress_physmmap_read()` performs volatile 64-bit reads.

Control flow: the stressor reads `--physmmap-read`, opens `/dev/mem`, builds the range list, synchronizes, and logs total pages for instance zero. Each pass attempts a whole-range mmap and then iterates every still-enabled page in each mappable range. Successful page mappings optionally read and are unmapped; failed pages are cleared from the bitmap. Ranges with no page successes become non-mappable. The loop stops when no ranges remain mappable or the run ends.

State and persistence behavior: state is heap range metadata and per-range bitmaps. Kernel state is transient `/dev/mem` mappings. No files are written.

Dependencies and integration points: Linux `/proc/iomem`, `/dev/mem`, `CAP_SYS_ADMIN`, mmap/munmap, stress-ng metrics, sync barriers, random flags, and `CLASS_VM` registration with `VERIFY_NONE`.

Risks: modern kernels often restrict `/dev/mem`, so inability to map pages is expected. Mapping physical RAM may be dangerous or denied depending on kernel config and lockdown mode. The range bitmap avoids retrying known failures, but whole-region attempts still occur each pass.

Test signals: privileged `--physmmap` should report total attempted pages and metrics for successful/failed mmaps and max pages mapped. Unprivileged runs should skip. `--physmmap-read` adds volatile read coverage for successful mappings.

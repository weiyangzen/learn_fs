# sources/test-tools/crashmonkey/code/user_tools/src/workload.cpp

Purpose: implements deterministic data-writing helpers for workload tests. It writes a 4 KiB repeated pattern at arbitrary offsets by either `pwrite` or mmap plus `msync`.

Important APIs/types/functions: `WriteData`, `WriteDataMmap`, static `kTestDataSize`, `kTestDataBlock`, compile-time `REP` macros, `pwrite`, `mmap`, `memcpy`, `msync`, and `munmap`. The pattern is `"abcdefghijklmnopqrstuvwxyz123456"` repeated to 4096 bytes.

Control flow: `WriteData` calculates the next 4 KiB boundary, writes an unaligned prefix if needed, writes full aligned pages, then writes a trailing partial range. `WriteDataMmap` maps the page-aligned covering range, copies the corresponding pattern bytes for unaligned and aligned segments, calls synchronous msync, and unmaps.

State/persistence behavior: direct writes change file data; mmap writes request persistence with `MS_SYNC`. The data pattern is offset-sensitive so later validators can infer correct placement.

Dependencies/integration: used by generated workloads and `WorkloadTest.cpp`. Risks/test signals: `WriteDataMmap` maps `size` rather than `map_size`, yet calls `msync/munmap` with `map_size`; this can be problematic for unaligned offsets. Tests currently focus on `WriteData`, not mmap.

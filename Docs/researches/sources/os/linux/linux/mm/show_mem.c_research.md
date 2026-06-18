# File Research: sources/os/linux/linux/mm/show_mem.c

Provides generic Linux memory summary and diagnostic reporting. It backs sysinfo-style memory totals, estimates available memory, and prints detailed free-area state for OOM/debug paths.

Key responsibilities:
- Defines/export global RAM counters `_totalram_pages`, `totalreserve_pages`, and `totalcma_pages`.
- Implements `si_mem_available()` by estimating free pages plus reclaimable page cache and reclaimable kernel memory, while preserving low-watermark reserves.
- Fills global `sysinfo` memory fields through `si_meminfo()`.
- Fills per-NUMA-node `sysinfo` memory fields through `si_meminfo_node()` when NUMA is enabled.
- Implements node filtering for `show_free_areas()` based on cpuset/nodemask flags.
- Prints global VM counters, per-node counters, per-zone watermarks and state, buddy free lists by order and migratetype, hugetlb node info, pagecache totals, and swap cache info.
- Implements `__show_mem()` to print the standard `Mem-Info` dump plus total RAM, highmem/movable-only pages, reserved pages, CMA pages, hardware-poisoned pages, and optional allocation profiling top users.

Important behavior:
- Available memory is an estimate, not an exact reclaim promise. It subtracts total reserves and keeps at least half of page cache/reclaimable memory or the low watermark.
- `SHOW_MEM_FILTER_NODES` suppresses nodes outside an explicit nodemask or the current cpuset memory allowance.
- Buddy free-list reporting samples protected zone state under each zone lock, then prints counts outside the lock.
- Output includes many conditional counters only when corresponding kernel features are enabled, such as THP, shadow call stack, zsmalloc, CMA, memory failure, and allocation profiling.

Dependencies:
- Uses VM statistics, zones/nodes, cpusets, highmem, block-device page accounting, hugetlb, swap cache reporting, CMA, allocation profiling codetags, and page allocator watermarks/free lists.

Notable risks:
- This is diagnostic code and intentionally tolerates races in global/per-node counters; exact consistency is less important than avoiding heavy locking during failures.
- Output format is consumed by humans and tooling, so field changes have operational visibility even though this is not a strict stable ABI.
- Allocation profiling output is guarded by a trylock to avoid recursive or contended diagnostic paths.

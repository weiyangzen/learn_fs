# File Research: sources/os/linux/linux/fs/proc/meminfo.c

## Scope

This file implements `/proc/meminfo`, the global memory and swap statistics report.

## Public And Internal APIs Covered

- Weak architecture hook: `arch_report_meminfo()`.
- Formatting helper: `show_val_kb()`.
- Display callback: `meminfo_proc_show()`.
- Init: `proc_meminfo_init()`.

## Control Flow And Behavior

- `meminfo_proc_show()` gathers `sysinfo`, swap info, committed memory, file cache estimate, LRU page counts, available memory, reclaimable slab, and unreclaimable slab.
- It emits core fields such as `MemTotal`, `MemFree`, `MemAvailable`, `Buffers`, `Cached`, `SwapCached`, active/inactive LRU splits, `Unevictable`, `Mlocked`, swap totals, dirty/writeback, anonymous/file/shmem mappings, slab, kernel stack, page tables, commit limit, vmalloc, percpu, balloon, GPU active/reclaim, and hugetlb data.
- Conditional sections report highmem, NOMMU mmap-copy pages, zswap, shadow call stack, memory failure, transparent huge pages, CMA, unaccepted memory, and architecture-specific lines.
- Init creates a permanent single-show proc entry named `meminfo`.

## Dependencies

- Depends on VM, swap, LRU, vmstat, hugetlb, zswap, CMA, memory failure, memtest, percpu, and architecture hooks.

## Risks And Invariants

- Values are snapshots from multiple counters and are not globally synchronized.
- `show_val_kb()` assumes page counts and shifts by `PAGE_SHIFT - 10`, so callers must pass page units unless they use explicit `seq_printf()` for already-kB counters.
- Userspace depends strongly on field names and rough formatting stability.

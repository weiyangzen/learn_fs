# File Research: sources/os/linux/linux-stable/fs/proc/meminfo.c

Implements `/proc/meminfo`.

Key points:
- Formats global memory, swap, LRU, slab, vmalloc, percpu, hugepage, zswap, CMA, THP, unaccepted memory, balloon, and GPU reclaim counters.
- Computes `Cached` from file pages minus swapcache and buffers.
- Uses `si_meminfo()`, `si_swapinfo()`, `vm_memory_committed()`, `si_mem_available()`, and VM stat counters.
- Provides weak `arch_report_meminfo()` extension hook.
- Registers `meminfo` as a permanent single proc file.

Dependencies/contracts:
- Text ABI consumed heavily by userspace tools.
- Feature-specific fields are gated by kernel config.

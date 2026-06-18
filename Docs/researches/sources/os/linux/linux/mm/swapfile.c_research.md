# File Research: sources/os/linux/linux/mm/swapfile.c

## Purpose
Implements swap device lifecycle, swap slot allocation/freeing/counting, swapoff unuse, swap extent mapping, discard/reclaim handling, hibernation swap helpers, `/proc/swaps`, and swapon/swapoff syscalls.

## Main Interfaces
- Allocation/counting: `folio_alloc_swap()`, `folio_dup_swap()`, `folio_put_swap()`, `swap_dup_entry_direct()`, `swap_put_entries_direct()`.
- Device refs: `get_swap_device()`, `put_swap_device()` via percpu refs.
- Cache freeing: `folio_free_swap()`, `__swap_cluster_free_entries()`.
- Swapoff: `try_to_unuse()`, `SYSCALL_DEFINE1(swapoff)`.
- Swapon: `SYSCALL_DEFINE2(swapon)`, `setup_swap_extents()`, `setup_swap_clusters_info()`.
- Extents and sectors: `add_swap_extent()`, `swap_folio_sector()`, `swapdev_block()`.
- Hibernation: `swap_alloc_hibernation_slot()`, `swap_free_hibernation_slot()`, `swap_type_of()`, `count_swap_pages()`.
- Accounting/output: `si_swapinfo()`, `/proc/swaps`.
- Initialization: `swapfile_init()`.

## Control Flow
Swapon allocates or reuses a `swap_info_struct`, opens the file/device, rejects unsupported files, reads and validates the swap header, builds swap extents, initializes cluster metadata and bad slots, allocates cgroup and zeromap state, configures discard/SSD/synchronous flags, initializes zswap, marks the inode `S_SWAPFILE`, sets priority, resurrects the percpu ref, and exposes the device on active/available priority lists.

Swap allocation first tries the current CPU’s cached cluster for the folio order, then rotates through priority-ordered available devices. HDD swap uses a per-device global cluster cursor; SSD swap uses per-CPU cursors. Clusters are kept on free, nonfull, fragmented, full, and discard lists. Allocation installs swap-cache PFN entries for folio-backed swapout or shadow placeholders for hibernation slots, updates usage counters, and removes full devices from the available list.

Counts are embedded in swap table entries up to `SWP_TB_COUNT_MAX`; larger counts use a per-cluster extension table. Decrementing counts batch-frees noncached slots and can reclaim cached slots when unmapped or swap is full.

Swapoff removes the device from allocation lists, waits for in-flight allocation locks, walks shmem and all process address spaces to replace swap PTEs with folios, drains residual swap-cache-only entries, kills the device percpu ref, waits for RCU and users, flushes discard/reclaim work, frees extents/cluster info/cgroup/zeromap/zswap state, clears `S_SWAPFILE`, and finally clears `SWP_USED`.

## State And Synchronization
Global `swap_lock` protects `swap_info`, active list, `SWP_USED`, `SWP_WRITEOK`, and total swap pages. `swap_avail_lock` protects the available priority list. Each cluster has its own lock for swap table/count/list-flag state. Per-device percpu refs prevent swapoff while entries are in use. Per-CPU cluster caches are protected by a local lock.

## Dependencies
Interacts with `swap_state.c` for cache entries, `swap_table.h` for slot encoding, `swap_cgroup.c`, zswap, memcg, shmem, KSM, rmap, PTE walking, block discard, filesystem `swap_activate`/`swap_deactivate`, security memory accounting, hibernation, procfs, and architecture swap hooks.

## Risks And Review Focus
- Lock ordering across `swap_lock`, `swap_avail_lock`, `si->lock`, cluster locks, and per-CPU local locks is central to correctness.
- Swapoff must prevent new allocations, handle reinserted entries under pressure, and wait for RCU/refcount users before freeing tables.
- Count overflow allocation can fail in atomic contexts and must roll back partial increments.
- Discard clusters are intentionally isolated from allocation until discard completes.
- Large folio allocation is restricted to block-device swap and same-order clusters.

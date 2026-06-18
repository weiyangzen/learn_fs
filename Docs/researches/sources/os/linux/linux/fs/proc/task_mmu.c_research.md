# File Research: sources/os/linux/linux/fs/proc/task_mmu.c

## Scope

This file implements MMU process memory proc interfaces: task memory summaries, `/proc/<pid>/maps`, `PROCMAP_QUERY`, `/proc/<pid>/smaps`, `/proc/<pid>/smaps_rollup`, `/proc/<pid>/clear_refs`, `/proc/<pid>/pagemap`, `PAGEMAP_SCAN`, and `/proc/<pid>/numa_maps`.

## Public And Internal APIs Covered

- Task memory helpers: `task_mem()`, `task_vsize()`, `task_statm()`.
- Maps operations: `proc_pid_maps_operations`.
- Smaps operations: `proc_pid_smaps_operations`, `proc_pid_smaps_rollup_operations`.
- Clear refs operations: `proc_clear_refs_operations`.
- Pagemap operations: `proc_pagemap_operations` under `CONFIG_PROC_PAGE_MONITOR`.
- NUMA maps operations: `proc_pid_numa_maps_operations` under `CONFIG_NUMA`.
- Ioctl implementations: `PROCMAP_QUERY` on maps and `PAGEMAP_SCAN` on pagemap.

## Control Flow And Behavior

- Basic memory summaries read MM counters for anon/file/shmem RSS, high-water values, locked/pinned pages, code/lib/data/stack, page-table bytes, swap, and hugetlb usage.
- The maps seq iterator pins the task and mm, chooses either mmap lock or per-VMA lock/RCU mode when configured, iterates VMAs plus the gate VMA sentinel, and tracks last position to survive VMA merge/restart cases.
- `show_map_vma()` prints maps-compatible ranges, permissions, offsets, device/inode, and path or synthetic names such as `[heap]`, `[stack]`, `[vdso]`, `[anon:name]`, and `[anon_shmem:name]`.
- `PROCMAP_QUERY` copies a versioned user struct, validates flags and optional buffers, finds a matching VMA by address and filters, fills range/flags/page size/file identity/name, optionally extracts a file build ID after dropping MM locks, and copies results back.
- Smaps uses page-table walks to accumulate RSS, PSS, clean/dirty private/shared memory, referenced, anonymous, KSM, lazyfree, THP, hugetlb, swap, swap PSS, and locked PSS.
- Smaps handles present PTEs, swap entries, device-private entries, transparent huge PMDs, hugetlb entries, and shmem holes/swap accounting.
- `show_smaps_rollup()` walks all VMAs into one aggregate, temporarily drops and reacquires `mmap_lock` under contention, and resumes carefully across VMA deletion, persistence, end-of-list, or split/merge overlap cases.
- `clear_refs_write()` parses values 1 through 5, pins the target mm, takes `mmap_write_lock`, then clears referenced/young bits, clears soft-dirty bits with write-protection and MMU notifier/TLB coordination, or resets high-water RSS.
- Pagemap encodes each virtual page into a 64-bit entry with PFN/swap offset when permitted, soft-dirty, exclusive, uffd-wp, guard, file, swapped, and present bits. PFNs are hidden unless the opener has `CAP_SYS_ADMIN` in `init_user_ns`.
- Pagemap walks in PMD-sized chunks, handles holes, PTEs, THPs, HugeTLB, migration/device/private marker entries, and copies buffered entries to userspace.
- `PAGEMAP_SCAN` validates scan masks, address ranges, optional output vector, and flags. It walks page tables, classifies pages by present/swapped/file/zero/huge/soft-dirty/guard/written/wp-allowed, coalesces output ranges, optionally write-protects matching pages for async userfaultfd, and writes back `walk_end`.
- NUMA maps walks each VMA, reports policy, file/heap/stack/huge tags, page counts by node, anon/dirty/mapped/mapmax/swapcache/active/writeback, and kernel page size.

## Dependencies

- Depends on MM page walkers, VMA iterators, mmap/per-VMA locking, ptrace-gated `proc_mem_open()`, folios, rmap/mapcount helpers, swap/softleaf entries, shmem, THP, HugeTLB, userfaultfd write-protect markers, MMU notifiers, TLB flushing, build-id parsing, mempolicy, and NUMA node state.

## Risks And Invariants

- All process memory interfaces must respect ptrace-style access checks through `proc_mem_open()`.
- Maps can run with per-VMA locking only for non-page-table-walking output; smaps and numa maps require mmap locking.
- Pagemap PFN disclosure is capability-gated because physical address information is an attack surface.
- Soft-dirty clearing and pagemap scan write-protection must coordinate with MMU notifiers and TLB flushing.
- Smaps and pagemap statistics are snapshots of mutable page tables; code handles races through locks, retries, and conservative treatment of non-present entries.

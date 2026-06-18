# File Research: sources/os/linux/linux-stable/fs/proc/task_mmu.c

Implements MMU-backed process memory proc files: `/proc/<pid>/maps`, `smaps`, `smaps_rollup`, `clear_refs`, `pagemap`, and `numa_maps`.

Key points:
- `task_mem()`, `task_vsize()`, and `task_statm()` provide process memory summaries for status/statm.
- Shared seq iteration over VMAs uses `proc_maps_private`; with `CONFIG_PER_VMA_LOCK`, plain maps can use per-VMA locks and RCU, while smaps/numa use `mmap_lock`.
- `show_map_vma()` formats maps lines and supports file paths, `[heap]`, `[stack]`, `[vdso]`, arch names, and named anonymous mappings.
- `PROCMAP_QUERY` ioctl on maps returns structured VMA info, optional VMA name, and optional ELF build ID.
- smaps:
  - walks PTE/PMD/hugetlb entries
  - accounts RSS, PSS, dirty/clean, referenced, anonymous, KSM, lazyfree, THP, hugetlb, swap, and locked memory
  - handles shmem swap efficiently where possible
  - prints `VmFlags` mnemonics and protection keys
- `smaps_rollup` aggregates across VMAs and temporarily releases/reacquires `mmap_lock` under contention with restart logic.
- `clear_refs` supports types 1-5: all, anon, mapped, soft-dirty, and reset high-water RSS; soft-dirty clearing write-protects PTEs/PMDs with MMU notifier/TLB handling.
- `pagemap`:
  - binary virtual-page-indexed `u64` records
  - hides PFNs unless caller has `CAP_SYS_ADMIN` in init user namespace
  - reports present, swapped, file/shared-anon, soft-dirty, exclusive, uffd-wp, and guard bits
  - handles THP and hugetlb specially
- `PAGEMAP_SCAN` ioctl scans ranges by page categories and can optionally write-protect matching pages for userfaultfd async WP.
- `numa_maps` reports policy, file/heap/stack markers, huge status, per-node page counts, dirty/active/writeback/swapcache/mapcount data.

Dependencies/contracts:
- Heavy coupling to mm page table walking, folios, rmap/mapcount, THP, hugetlb, shmem, swap, soft-dirty, userfaultfd, MMU notifiers, NUMA policy, ptrace access, and proc PID lifetime.
- Security-sensitive: pagemap PFN disclosure is capability-gated.

# File Research: sources/os/linux/linux/mm/khugepaged.c

## Role

Transparent Huge Page background collapse daemon and forced-collapse implementation. It scans eligible VMAs, collapses anonymous, shmem, and read-only file-backed ranges into PMD-sized folios, retracts PTE page tables for already-present THPs, exposes khugepaged sysfs controls, and starts/stops the khugepaged kthread based on THP policy.

## Key Data and Controls

- `enum scan_result` records detailed scan/collapse outcomes for tracepoints and `MADV_COLLAPSE` errno mapping.
- Sysfs attributes under the khugepaged group control:
  - `scan_sleep_millisecs`
  - `alloc_sleep_millisecs`
  - `pages_to_scan`
  - `pages_collapsed`
  - `full_scans`
  - `defrag`
  - `max_ptes_none`
  - `max_ptes_swap`
  - `max_ptes_shared`
- `khugepaged_scan` holds the global mm-slot cursor and next address.
- `mm_slots_hash` and `khugepaged_scan.mm_head` track address spaces registered for background scanning.
- `collapse_control` distinguishes khugepaged from forced collapse and tracks per-node source-page load plus allocation fallback mask.

## Registration and Thread Lifecycle

- `hugepage_madvise()` handles `MADV_HUGEPAGE` and `MADV_NOHUGEPAGE`; positive advice registers the VMA’s `mm` for scanning if eligible.
- `khugepaged_init()` creates the `mm_slot` cache and initializes defaults.
- `__khugepaged_enter()` allocates an `mm_slot`, inserts it behind the scan cursor, grabs an mm reference, and wakes the daemon if needed.
- `khugepaged_enter_vma()` registers only if PMD-sized THP is enabled and VMA policy allows khugepaged.
- `__khugepaged_exit()` removes or serializes with the active slot when an mm exits.
- `start_stop_khugepaged()` starts or stops the kthread as PMD THP policy changes and updates min-free-kbytes recommendations.
- `khugepaged()` loops through scans and sleeps, is freezable, runs at `MAX_NICE`, and cleans the current slot on stop.

## Anonymous Collapse

- `collapse_scan_pmd()` examines one PMD range:
  - skips unsuitable PMDs;
  - counts none/zero PTEs, swap PTEs, shared pages, and referenced pages;
  - rejects userfaultfd write-protected entries;
  - rejects non-anon, zone-device, lazyfree, pinned, locked, non-LRU, or badly NUMA-distributed pages;
  - requires enough referenced pages for khugepaged;
  - can allow limited missing/swap/shared PTEs based on sysfs thresholds.
- `__collapse_huge_page_swapin()` optionally swaps pages back in before collapse.
- `alloc_charge_folio()` allocates a PMD-sized folio on the selected node and charges memcg.
- `collapse_huge_page()` releases the read lock for allocation, revalidates the VMA, optionally swaps in pages, takes mmap write lock, invalidates MMU notifiers, clears the PMD, isolates source pages, copies into the new folio, deposits the old page table, maps the huge PMD, and traces success/failure.
- Copy failure due to machine-check-safe copy restores the original PMD and releases isolated pages.

## File/Shmem Collapse

- `collapse_scan_file()` scans the page cache range, counts present and swap entries, rejects unsuitable folios, builds node-load data, and calls `collapse_file()` if enough pages are present.
- `collapse_file()` allocates a new PMD-sized folio, locks old folios, handles shmem holes/swap/fallocate pages, performs file readahead for missing read-only file pages, rejects dirty/writeback file folios, isolates old folios, releases private data, unmaps mappings, validates refcounts, copies data, fills holes with zeroes, installs retry entries for shmem holes, checks userfaultfd missing-mode constraints, replaces xarray entries with one multi-index folio, updates LRU/accounting stats, retracts PTE tables, and frees or rolls back old folios.
- Read-only file THP handling increments/decrements mapping THP counts and uses barriers against writable opens.

## PTE-Mapped THP Retraction

- `try_collapse_pte_mapped_thp()` detects a PMD-sized folio already in the page cache but mapped through PTEs.
- It verifies all mapped PTEs point to the correct huge folio, invalidates MMU notifiers, clears PTEs, removes rmap and counters, collapses the empty PTE table, frees it deferred, and optionally installs a huge PMD.
- `collapse_pte_mapped_thp()` is the public wrapper.
- `file_backed_vma_is_retractable()` rejects MAP_PRIVATE VMAs with anon data, userfaultfd-wp ranges, and possible guard-marker VMAs.
- `retract_page_tables()` walks file mappings and removes empty retractable PTE tables after file/shmem collapse.

## Scanning Loop

- `collapse_single_pmd()` dispatches anonymous versus file-backed collapse and retries file writeback once for forced `MADV_COLLAPSE`.
- `collapse_scan_mm_slot()` walks VMAs in the current mm slot under a trylock mmap read lock, advances by PMD-sized ranges, handles dropped locks, removes dead/disabled slots, and traces progress.
- `khugepaged_do_scan()` drains LRU caches, scans up to `pages_to_scan`, sleeps after first hugepage allocation failure, and stops when no work remains.
- `khugepaged_wait_work()` sleeps according to scan interval or waits for new work/stop.

## Forced Collapse

- `madvise_collapse()` implements `MADV_COLLAPSE` over a VMA range.
- It uses a non-khugepaged `collapse_control`, drains LRU caches, collapses each PMD-aligned subrange, reacquires mmap lock after dropped-lock paths, and returns actionable errno values through `madvise_collapse_errno()`.
- Forced collapse is less restricted by khugepaged reference thresholds but still respects VMA suitability and hard safety checks.

## Dependencies

Uses THP policy, VMA iteration, mmap locks, anon-vma locking, MMU notifiers, rmap, swap fault handling, shmem, xarray page cache, DAX/file writeback checks, userfaultfd, KSM zero-page handling, LRU isolation, memcg charging, page-table allocation/freeing, tracepoints from `trace/events/huge_memory.h`, and `mm_slot` infrastructure.

## Research Notes

This file is the central PMD-sized THP collapse engine. Its main invariants are repeated VMA/PMD revalidation after dropped locks, strict exclusion of pinned or unstable pages, MMU notifier coverage around page-table removal, and rollback paths for copy or page-cache replacement failures. Background khugepaged and synchronous `MADV_COLLAPSE` share most machinery but differ in thresholds, retry behavior, and returned failure semantics.

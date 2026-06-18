# File Research: sources/os/linux/linux/mm/mapping_dirty_helpers.c

Shared mapping dirty-tracking helpers for write-protecting and cleaning PTEs over an `address_space` page-offset range.

Key responsibilities:
- Provides `wp_shared_mapping_range()` to write-protect writable PTEs mapping a shared address-space range.
- Provides `clean_record_shared_mapping_range()` to clear dirty PTEs and record dirty page offsets in a caller bitmap.
- Defines page-walk state for write-protect and clean-record operations, including compact TLB flush ranges.
- Coordinates cache flushing, MMU notifier invalidation, TLB pending accounting, and range TLB flushing around page-table modifications.

Important behavior:
- `wp_pte()` checks each PTE and converts writable entries to read-only with `ptep_modify_prot_start()`/`commit()`, counting only PTEs actually changed.
- `clean_record_pte()` clears dirty PTEs, records the corresponding mapping page offset in the bitmap, and updates first/last modified bitmap bounds.
- PMD/PUD callbacks deliberately do not split transparent huge entries; they warn if huge entries are writable or dirty because tracking is PTE-level.
- `wp_clean_test_walk()` skips VMAs that are not shared, not may-write, or are hugetlb.
- `wp_clean_pre_vma()` initializes MMU notifier range, starts invalidation, flushes caches, initializes the touched TLB range, and increments pending TLB flush state.
- `wp_clean_post_vma()` flushes either the full notifier range for nested TLB flushes or the compact modified subrange, then ends notifier invalidation and decrements pending TLB state.
- Both exported functions hold `i_mmap_lock_read(mapping)` while walking all VMAs mapping the address-space range.
- `clean_record_shared_mapping_range()` guarantees dirty PTEs observed at start are recorded, while racing new dirties may remain dirty, be recorded, or both.

Dependencies:
- Uses `walk_page_mapping()` and `struct mm_walk_ops`.
- Depends on PTE modification helpers, THP PMD/PUD inspection, MMU notifier ranges, cache flushes, TLB flush APIs, and address-space interval locking.
- Intended for subsystems doing PTE-level dirty tracking over shared mappings.

Notable risks:
- Huge PMD/PUD entries are skipped rather than split, so callers needing complete hugepage dirty tracking need additional handling.
- Dirty recording is race-aware but not a full synchronization barrier against new writers; callers needing a closed dirty snapshot must first write-protect and block page-mkwrite/pfn-mkwrite paths.
- Bitmap indexing assumes the provided bitmap covers the requested mapping range relative to `bitmap_pgoff`.
- The functions `WARN_ON()` unexpected page-walk failures but otherwise return the number of PTEs modified.

# File Research: sources/os/linux/linux-stable/fs/dax.c

## Summary
Implements filesystem DAX support for page-cache-like exceptional entries, direct persistent-memory I/O, DAX mmap faults, writeback/cache flushing, layout breaking, zeroing/truncation, unshare/CoW handling, dedupe comparison, and remap preparation. It uses XArray value entries to represent locked/empty/zero/real DAX mappings at PTE or PMD granularity.

## Main Responsibilities
- Define and manage DAX XArray entry encoding for lock state, PMD size, zero pages, and empty placeholders.
- Provide wait queues and locking helpers for DAX exceptional entries.
- Associate and disassociate DAX folios with address spaces, including shared-folio tracking.
- Reset compound DAX folios to order-0 state when mappings are removed.
- Lock DAX entries by folio or mapping/index for memory-management users.
- Grab or create locked mapping entries, including PMD-to-PTE downgrade behavior.
- Detect busy pinned DAX pages before layout changes.
- Invalidate/delete DAX entries and clear dirty/writeback tags.
- Break DAX layouts by unmapping mappings, waiting for DMA/pins, and deleting entries.
- Copy around unaligned writes and CoW edges.
- Implement DAX reads/writes through iomap and direct persistent-memory access.
- Handle PTE and PMD DAX faults, holes, zero pages, synchronous faults, CoW faults, and write faults.
- Flush dirty DAX ranges to the persistent domain for data-integrity writeback.
- Support DAX zeroing, truncate-page zeroing, file unshare, dedupe comparison, and remap prep.

## Key APIs
- `dax_folio_reset_order()`
- `dax_lock_folio()` / `dax_unlock_folio()`
- `dax_lock_mapping_entry()` / `dax_unlock_mapping_entry()`
- `dax_layout_busy_page_range()` and `dax_layout_busy_page()`
- `dax_delete_mapping_entry()` and `dax_delete_mapping_range()`
- `dax_break_layout()` and `dax_break_layout_final()`
- `dax_invalidate_mapping_entry_sync()`
- `dax_file_unshare()`
- `dax_zero_range()` and `dax_truncate_page()`
- `dax_iomap_rw()`
- `dax_iomap_fault()`
- `dax_finish_sync_fault()`
- `dax_dedupe_file_range_compare()`
- `dax_remap_file_range_prep()`
- `dax_writeback_mapping_range()`

## Important Behavior
DAX entries are XArray value entries, not normal page-cache pages. Four low bits encode locked, PMD, zero-page, and empty-entry state; the remaining bits carry the PFN. Entry locking is serialized through the mapping XArray lock plus hashed wait queues keyed by XArray and aligned entry start.

PTE entries are favored over PMD entries. PMD zero or empty entries can be downgraded when a PTE entry is needed. Real PMD storage entries are not evicted merely to upgrade/downgrade; PTE writes can dirty the whole PMD entry as appropriate.

DAX folio association tracks whether a persistent-memory folio belongs to one mapping or has become shared across mappings. Shared folios clear `mapping` and use `share`; removal decrements sharing, resets compound state, restores pgmap pointers, and verifies sub-folio refcounts.

Layout breaking first unmaps mappings to stop new fast GUP pins, scans DAX entries for busy pages, waits for pins/DMA when a callback is supplied, and deletes mapping entries once no busy page remains. NOWAIT callers can pass no callback and receive `-ERESTARTSYS` on the first busy page.

Fault handling uses iomap to resolve storage. Read faults on holes install zero pages; write faults allocate or CoW real storage; `MAP_SYNC` synchronous faults can return `VM_FAULT_NEEDDSYNC` with a PFN for later insertion after `fsync`. PMD faults fall back unless alignment, VMA range, EOF, and CoW constraints are satisfied.

Writeback tags DAX entries to write, write-protects all VMAs mapping the PFN range, flushes CPU caches to the persistent domain, then clears dirty tags while holding the entry lock so concurrent faults cannot dirty the same PFN between protection and flush completion.

## Research Notes
This file is a central coordination layer among iomap, XArray, MM faults, ZONE_DEVICE pages, persistent-memory flushing, GUP/DMA exclusion, and filesystem layout changes. The most important invariants are locked-entry wakeups, dirty/writeback tag ordering, PMD/PTE granularity rules, folio sharing metadata, and caller-provided filesystem locking around faults, truncate, punch hole, and direct I/O.

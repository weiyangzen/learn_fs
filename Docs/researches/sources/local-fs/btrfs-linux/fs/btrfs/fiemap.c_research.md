# File Research: sources/local-fs/btrfs-linux/fs/btrfs/fiemap.c

## Scope

This file implements Btrfs FIEMAP reporting for regular files. It walks file extent items, reports inline, regular, compressed, shared, preallocated, hole, and delalloc ranges, merges compatible adjacent FIEMAP records, buffers emitted entries to avoid self-deadlocks, and coordinates with ordered extents and the inode IO tree for a stable enough view of file layout.

## Main APIs And Entry Points

- `btrfs_fiemap()` is the public entry point called by inode operations. It performs generic FIEMAP preparation, optional sync/writeback waiting, inode shared locking, and delegates to `extent_fiemap()`.
- `extent_fiemap()` performs the main scan over the requested range, locks the inode IO-tree range, finds the last meaningful extent, searches the subvolume tree for file extent items, processes holes and extents, handles cache flushing/restart, and emits final buffered entries.
- `emit_fiemap_extent()` merges or buffers FIEMAP extents and signals when the intermediate buffer must be flushed.
- `flush_fiemap_cache()` and `emit_last_fiemap_cache()` write buffered entries to the user FIEMAP buffer.
- `fiemap_search_slot()` finds the first relevant file extent item and clones the leaf for long processing.
- `fiemap_next_leaf_item()` advances within or across leaves while reusing a cloned leaf when possible.
- `fiemap_process_hole()` reports delalloc inside holes or prealloc extents and reports unwritten portions of prealloc extents.
- `fiemap_find_last_extent_offset()` finds the end of the last non-hole file extent item so the last returned extent can receive `FIEMAP_EXTENT_LAST`.

## Control Flow And Behavior

`btrfs_fiemap()` first calls `fiemap_prep()`. If `FIEMAP_FLAG_SYNC` is set, it waits for all ordered extents before taking the inode shared lock, then waits again after the lock because new writes may have started between the initial flush and locking. This is necessary for compression: the generic write-and-wait can start async compression without waiting for compressed writeback and ordered extent completion.

`extent_fiemap()` rounds the requested range to sectorsize boundaries and locks that inode IO-tree range. It finds the last extent end independently from i_size because preallocation can extend past EOF. It then searches for the first file extent item at or before the requested range. The btree leaf is cloned so expensive backref sharedness checks and user-buffer emission do not keep a live subvolume tree leaf locked for too long or trigger lockdep recursion during backref walking.

The main loop processes implicit holes before the current file extent item, then handles the item by type. Inline extents are reported with DATA_INLINE and NOT_ALIGNED. Regular extents report physical bytenr plus file extent offset, and compressed extents add ENCODED while avoiding uncompressed offset adjustment. Prealloc extents and explicit holes are delegated to `fiemap_process_hole()`, which searches the io_tree for delalloc ranges and emits DELALLOC|UNKNOWN records where dirty delayed allocation exists.

Preallocated extents are split for reporting: unwritten sections are emitted with FIEMAP_EXTENT_UNWRITTEN, while delalloc subsections are emitted as DELALLOC|UNKNOWN. Sharedness for regular and prealloc extents is computed with `btrfs_is_data_extent_shared()` only when the user requested actual extents (`fi_extents_max` nonzero); the result adds FIEMAP_EXTENT_SHARED.

`emit_fiemap_extent()` caches one pending extent and merges adjacent entries only when logical addresses, physical addresses, and flags are continuous/equal. It also handles races where the scan had to unlock and restart: newly completed ordered extents can split or replace previously observed delalloc/hole/prealloc ranges, so the cache trims, discards, or partially advances entries to avoid overlapping FIEMAP output.

The intermediate entry array prevents deadlock when the user's FIEMAP buffer is mmaped from the same file. Writing to that buffer may fault through `btrfs_page_mkwrite()` and try to lock the same inode extent range. Therefore `extent_fiemap()` flushes buffered entries only after unlocking the io_tree range and releasing the path. If the cache fills while scanning, it returns the private `BTRFS_FIEMAP_FLUSH_CACHE` sentinel, flushes entries, updates `start/len` to `next_search_offset`, and restarts.

At EOF, if the cached entry reaches the last non-hole extent end and there is no later delalloc before i_size, `FIEMAP_EXTENT_LAST` is added. The final path is freed before flushing to user memory for the same deadlock avoidance reason.

## State And Data Structures

- `struct btrfs_fiemap_entry` is the buffered output tuple: logical offset, physical address, length, and FIEMAP flags.
- `struct fiemap_cache` stores the intermediate entries array, fill position, next restart offset, mapped extent count, and one cached unsubmitted extent.
- `BTRFS_FIEMAP_FLUSH_CACHE` is a private non-errno sentinel telling the caller to unlock, flush buffered entries, and restart scanning.
- `btrfs_backref_share_check_ctx` is reused across sharedness checks and tracks the current cloned leaf bytenr for optimization.
- Cached `extent_state` pointers are used for the locked FIEMAP range and delalloc searches.

## Dependencies

This file depends on Btrfs inode locking, io_tree extent locking, file extent item accessors, path/leaf navigation, extent-buffer cloning/copying, delalloc range search, ordered extent waiting, backref sharedness checks, generic FIEMAP helpers, and kernel signal/reschedule handling.

## Risks And Invariants

- FIEMAP must not emit overlapping extents even when ordered extents complete after the scan unlocks and restarts.
- User-buffer writes must happen after releasing inode extent locks and btree paths, because the buffer may be mmaped from the target file and fault back into Btrfs.
- The cloned leaf's `start` must be set before copying contents, especially for subpage metadata where `start` affects EB folio offset calculations.
- Sharedness checks can be expensive and can lock tree blocks; using a cloned leaf avoids holding live tree locks during that work.
- `FIEMAP_EXTENT_LAST` must account for prealloc past i_size and delalloc after the last file extent.
- `FIEMAP_FLAG_SYNC` requires ordered extent completion beyond generic filemap writeback, particularly for compressed writes.

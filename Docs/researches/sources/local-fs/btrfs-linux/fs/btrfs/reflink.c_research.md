# File Research: sources/local-fs/btrfs-linux/fs/btrfs/reflink.c

This file implements Btrfs `remap_file_range`, covering clone/reflink and dedupe operations. It validates VFS remap requests, locks source and destination inodes/ranges, flushes ordered extents so file extent items are stable, clones regular/prealloc extents by reference, handles inline extents, replaces holes, updates inode metadata, and performs sync handling for synchronous files.

Public entry point:
- `btrfs_remap_file_range()` is exported through `reflink.h` and installed in `file.c` as `.remap_file_range`.
- It supports `REMAP_FILE_DEDUP` and `REMAP_FILE_ADVISORY`; any other remap flags return `-EINVAL`.
- It rejects shutdown filesystems, locks one inode for same-file remaps or both non-directory inodes for cross-file remaps, and takes the involved Btrfs mmap locks in a stable order.

Request preparation:
- `btrfs_remap_file_range_prep()` enforces Btrfs-specific constraints before delegating to `generic_remap_file_range_prep()`.
- Non-dedupe clone checks the destination root is writable.
- Source and destination must either both be encrypted or both unencrypted.
- Source and destination must match `BTRFS_INODE_NODATASUM`; the destination must not become partly checksummed.
- The function explicitly flushes source mapping writeback and waits for ordered extents in source and destination ranges, because Btrfs needs compression writeback and ordered extent completion, not just bio completion.
- It flushes the whole source inode mapping first so buffered NOCOW writes reach disk as NOCOW before extent refs are increased.

Clone implementation:
- `btrfs_clone_files()` adjusts EOF-block length to sector alignment, expands the destination with `btrfs_cont_expand()` when cloning beyond EOF, waits for writeback over the old EOF area, locks the destination extent range, calls `btrfs_clone()`, waits for any inline-data delalloc completion, invalidates destination page cache, and balances dirty btrees.
- `btrfs_clone()` walks source file extent items from `off` through the aligned clone length. It handles previous extents that overlap the start, implicit holes with `NO_HOLES`, regular/prealloc extents, inline extents, and trailing implicit holes.
- Regular and prealloc extents are cloned via `btrfs_replace_file_extents()` with `struct btrfs_replace_extent_info`, after trimming leading/trailing portions outside the requested source range.
- Holes are cloned by calling `btrfs_replace_file_extents()` with a `NULL` clone info over the destination hole range.
- After each cloned extent or hole, `clone_finish_inode_update()` updates i_version, times unless suppressed, i_size, safe disk i_size, inode item, and ends the transaction.

Inline extent handling:
- `clone_copy_inline_extent()` tries to clone an inline extent item directly only when the destination offset is 0 and the destination file shape allows replacing/inserting an inline item.
- If inline direct insertion is unsafe or impossible, it falls back to `copy_inline_to_page()`.
- `copy_inline_to_page()` reserves delalloc space, gets/creates the destination folio, sets extent mapping and delalloc state, sets `BTRFS_INODE_NO_DELALLOC_FLUSH` to avoid transaction/delalloc deadlocks, copies or decompresses inline data, zero-fills the rest of the sector when the inline data is short, marks the folio uptodate/dirty, and releases reservations on error.
- The code may increase destination `i_size` before starting a transaction after copying inline data beyond EOF to avoid a flush-on-commit deadlock involving folio invalidation and extent locks.

Dedupe implementation:
- `btrfs_extent_same()` wraps dedupe with `root_dst->dedupe_in_progress` and rejects dedupe into a root with send in progress.
- It chunks dedupe work into `BTRFS_MAX_DEDUPE_LEN` (16 MiB) segments.
- `btrfs_extent_same_range()` locks the destination extent range, calls `btrfs_clone()` with `no_time_update = true`, unlocks, and balances dirty btrees.
- Data equality checking and generic dedupe range validation are delegated to VFS `generic_remap_file_range_prep()` after Btrfs-specific flushing and constraints.

Locking and synchronization:
- `btrfs_double_mmap_lock()` and `btrfs_double_mmap_unlock()` acquire two Btrfs mmap locks in pointer order with nested locking annotations.
- Destination extent locks serialize with readahead and protect the range while file extent items are replaced.
- Source mmap locks protect against relocation interactions described in comments.
- `BTRFS_INODE_NO_DELALLOC_FLUSH` is set only around inline-to-page clone work and cleared on every `btrfs_clone()` exit.
- Synchronous source or destination files trigger `btrfs_sync_file()` on both source and destination ranges after successful remap so reflinked data is durable after power loss.

Fsync and metadata correctness:
- `btrfs_clone()` updates `last_reflink_trans` on the destination for every cloned extent/hole/inline operation.
- It updates the source inode’s `last_reflink_trans` when a newly generated, non-hole, non-inline extent is shared, preventing fsync checksum logging overlap problems.
- Replacing inline extents and some hole cases set full-sync state with `btrfs_set_inode_full_sync()`.
- `clone_finish_inode_update()` rounds the final inode size to the user-requested clone length rather than the internally aligned clone length.

Cross-file relationships:
- `file.c` exposes this implementation through `btrfs_file_operations.remap_file_range`.
- `inode.c` provides `btrfs_cont_expand()`, inode update helpers, inode locking helpers, ordered extent waiting, file extent range tracking, and inode byte accounting used here.
- `file-item.c` / `accessors.h` provide file extent item accessors and checksum-sensitive metadata helpers.
- `delalloc-space.c`, `extent-io-tree.c`, `subpage.h`, and compression code support inline-to-page fallback.
- `transaction.c` and extent replacement/drop helpers provide the transactional file extent changes.

Important invariants and risks:
- All clone/dedupe ranges are sector-aligned except permitted EOF behavior handled by VFS prep and internal alignment.
- Reflink must not mix encryption state or checksum policy between source and destination.
- Ordered extent completion must finish before cloning refs, otherwise the file extent items and checksums being shared may not exist or may still change.
- Inline extents have special constraints: they start at offset 0, fit within the sectorsize, and cannot be partially cloned.
- Destination page cache is invalidated after clone so reads see the new shared extents rather than stale cached data.
- Send and dedupe are coordinated with `dedupe_in_progress` / `send_in_progress` to avoid changing a root while send is using it.
- The code intentionally releases btree paths before starting transactions or reserving delalloc space to avoid lockdep problems and real deadlocks.

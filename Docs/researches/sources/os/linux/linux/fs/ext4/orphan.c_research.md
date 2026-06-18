# File Research: sources/os/linux/linux/fs/ext4/orphan.c

## Purpose
Manages ext4 orphaned inodes: unlinked-but-open files and inodes needing crash-safe truncate completion. Supports both the classic superblock-linked orphan list and the newer orphan-file feature.

## Main Entry Points
- `ext4_orphan_add()` links an inode into orphan tracking.
- `ext4_orphan_del()` removes an inode from orphan tracking.
- `ext4_orphan_cleanup()` performs mount-time recovery cleanup.
- `ext4_init_orphan_info()` / `ext4_release_orphan_info()` initialize and release orphan-file state.
- `ext4_orphan_file_empty()` reports whether the orphan file has any live entries.

## Orphan File Path
`ext4_orphan_file_add()` chooses a starting orphan-file block using CPU-based hashing, atomically reserves a free entry counter, journals the block, finds a zero slot using `cmpxchg()`, records `i_orphan_idx`, sets `EXT4_STATE_ORPHAN_FILE`, and dirties metadata. It falls back to the classic list on `-ENOSPC`. `ext4_orphan_file_del()` journals the containing orphan-file block, clears the slot, increments the free-entry counter, clears state, and reinitializes the in-memory list node.

## Classic Orphan List Path
When the orphan file is unavailable or full, `ext4_orphan_add()` journals the superblock and inode, inserts the inode at `s_last_orphan`, updates the in-memory `s_orphan` list under `s_orphan_lock`, and rolls back the in-memory list if on-disk dirtying fails. `ext4_orphan_del()` removes from the in-memory list, updates either `s_last_orphan` or the previous orphan inode’s `NEXT_ORPHAN`, and clears the removed inode’s next pointer.

## Recovery Flow
`ext4_orphan_cleanup()` skips unsafe cases: no orphans, readonly block device, unknown incompatible feature state, or filesystem error state. It temporarily enables writes for readonly mounts and turns on quotas if needed. It walks the classic orphan chain from `s_last_orphan` and scans every orphan-file slot. `ext4_process_orphan()` truncates linked inodes or lets final `iput()` delete unlinked ones.

## Integrity
Orphan-file initialization validates the special orphan inode, caps maximum orphan-file size at `EXT4_MAX_ORPHAN_FILE_BLOCKS`, pins block buffers, validates magic and metadata checksums, and records per-block free-entry counters. Checksum calculation includes the orphan block number and data entries.

## Integration Points
Uses JBD2 metadata journaling, inode dirtying, quota setup, mount-state flags, ext4 special inode lookup, checksum helpers, buffer heads, and orphan recovery helpers such as `ext4_orphan_get()` and `ext4_truncate()`.

## Invariants and Risks
Orphan state must be crash-consistent before link counts or truncate state become unrecoverable. In-memory list updates must not leave stray entries on failure. The orphan-file free-entry counters are performance aids but must remain synchronized with slot clearing/allocation. Recovery intentionally tolerates stale/corrupt orphan references because fsck may already have cleaned them.

## Testing Signals
Test classic list fallback, orphan-file slot exhaustion, checksum/magic failure at mount, quota-enabled cleanup, readonly mount cleanup, failed truncate cleanup, and unlink/truncate crash recovery.

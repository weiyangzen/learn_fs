# File Research: sources/os/linux/linux-stable/fs/ext4/orphan.c

## Summary
Implements ext4 orphan inode tracking and recovery. It supports both the legacy superblock-linked orphan inode list and the newer orphan-file feature, cleans up orphaned inodes during mount recovery, and validates/checksums orphan-file blocks.

## Main Responsibilities
- Add inodes being truncated or unlinked to durable orphan tracking.
- Remove inodes from orphan tracking after cleanup completes.
- Maintain in-memory orphan lists and on-disk orphan metadata consistently.
- Use orphan-file slots when available, falling back to the legacy linked list on space exhaustion.
- Recover orphaned inodes after crash by truncating linked inodes and deleting unlinked inodes.
- Temporarily enable quotas during orphan cleanup when required.
- Initialize, verify, checksum, and release orphan-file block state.

## Key Data and State
- `EXT4_STATE_ORPHAN_FILE`: marks an inode tracked through the orphan file.
- `EXT4_I(inode)->i_orphan_idx`: slot index in the orphan file.
- `EXT4_SB(sb)->s_orphan`: in-memory orphan list.
- `EXT4_SB(sb)->s_orphan_lock`: serializes legacy orphan-list updates.
- `struct ext4_orphan_info`: per-superblock orphan-file block array, checksum seed, and free-entry counters.
- `struct ext4_orphan_block`: pinned orphan-file block plus atomic free-entry count.

## Key Functions
- `ext4_orphan_file_add()`: chooses an orphan-file block using a CPU-based start offset, reserves a free-entry count atomically, journals the block, finds a zero slot with `cmpxchg()`, stores the inode number, and marks inode orphan-file state.
- `ext4_orphan_add()`: public add path; validates journal and inode state, tries orphan-file tracking first, then inserts the inode at the head of the legacy on-disk orphan list and in-memory list.
- `ext4_orphan_file_del()`: clears an orphan-file slot, increments its free counter, dirties the orphan-file block, and clears in-memory orphan state.
- `ext4_orphan_del()`: removes an inode from orphan-file or legacy orphan tracking; for the legacy list, updates either the superblock `s_last_orphan` or previous inode `NEXT_ORPHAN`.
- `ext4_process_orphan()`: recovery helper that truncates linked orphan inodes or drops unlinked orphan inodes with `iput()`.
- `ext4_orphan_cleanup()`: mount-time cleanup over both legacy `s_last_orphan` chain and orphan-file entries, with read-only/error-state handling and quota enable/disable.
- `ext4_release_orphan_info()`: releases pinned orphan-file buffers and arrays.
- `ext4_orphan_file_block_csum_verify()` and `ext4_orphan_file_block_trigger()`: verify and update orphan-file block checksums.
- `ext4_init_orphan_info()`: opens the orphan-file inode, bounds its size, reads and validates each orphan-file block, verifies magic/checksum, and initializes free counters.
- `ext4_orphan_file_empty()`: checks whether all orphan-file slots are free.

## Recovery Behavior
If a filesystem has orphaned inodes and is mountable read-write, cleanup temporarily clears read-only state if needed, enables quota accounting as needed, then processes:
- Legacy linked-list orphans from `es->s_last_orphan`.
- Orphan-file entries from every pinned orphan-file block.

Linked inodes are truncated to their recorded size; unlinked inodes are deleted when the final `iput()` drops them. If the filesystem is already in error state, recovery avoids normal cleanup and may clear the legacy list on writable mounts.

## Synchronization and Journaling
- Legacy orphan list updates are serialized by `s_orphan_lock`.
- Orphan-file slot allocation uses atomic free-entry counters and `cmpxchg()` on slot contents.
- All on-disk orphan metadata changes require journal write access and dirty metadata calls.
- Callers are expected to hold inode `i_rwsem` unless the inode is newly created or being deleted.
- In-memory list removal happens even when an error path lacks a usable transaction handle.

## Dependencies
Uses ext4 inode write reservation/dirtying, superblock checksum updates, jbd2 metadata journaling, quota initialization and quota-on-mount paths, orphan-file checksum triggers, and ext4 inode lookup during recovery.

## Risks and Edge Cases
- Orphan-file slot search can race with other allocations/frees; the loop is bounded to avoid indefinite spinning and falls back to the legacy list.
- Failed legacy orphan-list metadata updates require removing the inode from the in-memory list to avoid unmount-time panics.
- Recovery must not run on unsuitable read-only devices, unsupported feature sets, or filesystems already marked erroneous.
- Orphan-file size is capped to avoid excessive memory pinning on corrupted filesystems.

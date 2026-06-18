# File Research: sources/os/linux/linux/fs/ocfs2/quota_local.c

`quota_local.c` implements the per-slot local quota files used by OCFS2 nodes to accumulate quota deltas before syncing them to the global quota files. It owns local quota file layout, chunk bitmaps, local dquot allocation, and crash recovery.

Main responsibilities:
- Defines local quota layout helpers:
  - entries per block, blocks per chunk, chunk header block, dquot block, and byte offsets.
  - chunks contain a header bitmap plus one or more blocks of `ocfs2_local_disk_dqblk` entries.
- Provides `ocfs2_modify_bh()` as a small journaling wrapper for modifying local quota buffers.
- Reads quota blocks with `ocfs2_read_quota_block()`, validating file bounds and ECC through the shared quota validator.
- Validates quota file format in `ocfs2_local_check_quota_file()` for both local and global quota headers, magic values, and versions.
- Loads and releases in-memory chunk bitmap state with `ocfs2_load_local_quota_bitmaps()` and `ocfs2_release_local_quota_bitmaps()`.
- Implements quota crash recovery:
  - `ocfs2_begin_quota_recovery()` scans another slot’s local quota files after journal replay, recording non-empty chunk bitmaps in memory.
  - `ocfs2_recover_local_quota_file()` walks recorded local entries, gets the corresponding global dquot, applies local space/inode deltas, releases the dead node’s global dquot use count, and frees the local entry bitmap bit.
  - `ocfs2_finish_quota_recovery()` locks each recovered local quota file, replays needed deltas, and marks the file clean if it belongs to another slot.
- Implements local quota format operations:
  - `ocfs2_local_read_info()` allocates `ocfs2_mem_dqinfo`, reads global info first, locks the local quota inode, loads chunk bitmaps, records unclean-file recovery work, and marks the local file in-use by clearing `OLQF_CLEAN`.
  - `ocfs2_local_free_info()` checks all entries are free, releases lock resources, marks the local file clean when safe, and tears down private info.
  - `ocfs2_local_write_info()` persists local info fields.
- Writes local dquot deltas through `ocfs2_local_write_dquot()`, storing only differences from original global usage.
- Allocates and frees local dquot entries:
  - `ocfs2_find_free_entry()` searches chunk bitmaps.
  - `ocfs2_local_quota_add_chunk()` grows the local quota file by a new chunk header and data block.
  - `ocfs2_extend_local_quota_file()` adds a data block to the final chunk when possible.
  - `ocfs2_create_local_dquot()` reserves a free local entry, maps its physical block, initializes it, and sets the chunk bitmap bit.
  - `ocfs2_local_release_dquot()` clears the entry bit during global dquot release.

Key invariants:
- Local quota files are protected by their inode cluster lock and by `ip_alloc_sem` during entry allocation/growth.
- `OLQF_CLEAN` is cleared while a node is actively using a local quota file; unclean files trigger recovery.
- Recovery records bitmaps before replay, so local entries can be folded into global quota state even after node failure.
- Local entries store deltas, not full authoritative quota usage; global files remain the cluster-wide source of truth.

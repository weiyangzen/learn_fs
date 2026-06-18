# File Research: sources/local-fs/ocfs2-tools/libocfs2/quota.c

Implements userspace OCFS2 quota metadata handling, quota usage computation, cached dquot management, and global/local quota file initialization.

Endian and ECC:
- Swap helpers cover quota headers, local quota info, local chunk headers, global quota info, global dquot records, and quota tree leaf headers.
- `ocfs2_checksum_quota_block()` computes metadata ECC in the quota block trailer.
- `read_blk()` reads from the global quota file and validates trailer ECC.
- `write_blk()` recomputes trailer ECC and writes the full block.

Quota hash cache:
- `ocfs2_new_quota_hash()` creates an 8192-bucket hash.
- Buckets are power-of-two indexed by `id * 5`.
- `ocfs2_insert_quota_hash()` doubles buckets when used entries exceed allocated entries, capped at `1 << 21`.
- Find/create/read helpers cache `ocfs2_cached_dquot` records.
- `ocfs2_write_release_dquots()` iterates cached dquots, clears grace timers when usage is below soft limits, writes each dquot, removes it from the hash, and frees it.
- `ocfs2_free_quota_hash()` refuses to free non-empty hashes.

Usage computation:
- `ocfs2_compute_quota_usage()` scans every inode via `ocfs2_open_inode_scan()` and `ocfs2_get_next_inode()`.
- It filters by inode signature, generation, valid flag, and excludes system files except the root inode.
- It accumulates current space as allocated clusters converted to bytes and increments inode counts for UID and/or GID hashes.

Quota change workflow:
- `ocfs2_init_quota_change()` allocates user/group hashes only when corresponding ro-compat quota features are enabled.
- `ocfs2_apply_quota_change()` reads or creates affected UID/GID dquots and applies signed space/inode deltas.
- `ocfs2_finish_quota_change()` writes/releases hashes and frees them.

Local quota files:
- `ocfs2_init_local_quota_file()` validates the system quota inode, ensures at least two blocks, sets inode size/mtime, writes local quota header and info, initializes clean flags, checksums both initial blocks, and writes through file I/O.
- `ocfs2_init_local_quota_files()` initializes every per-slot local user/group quota file after truncating it.

Global quota info and files:
- `ocfs2_qtree_depth()` computes qtree depth from block size and 32-bit quota IDs.
- `ocfs2_qtree_index()` selects qtree child indexes by depth.
- `ocfs2_init_fs_quota_info()` locates and caches global user/group quota system inodes.
- `ocfs2_read_global_quota_info()` and `ocfs2_write_global_quota_info()` load/store global header and info.
- `ocfs2_load_fs_quota_info()` loads enabled user/group quota info.
- `ocfs2_init_global_quota_file()` initializes the global quota file with two blocks, header, info block, qtree root, inode size, and dirty flags.

Global quota qtree:
- Free block list is managed by `ocfs2_get_free_dqblk()` and `ocfs2_put_free_dqblk()`.
- Blocks with free dquot slots are managed by `ocfs2_insert_free_dqentry()` and `ocfs2_remove_free_dqentry()`.
- `ocfs2_find_free_dqentry()` chooses or creates a leaf block, increments entry count, locates an unused dquot slot, writes the leaf, and returns a byte offset.
- `ocfs2_do_insert_tree()` recursively creates qtree internal blocks and leaf dquot references.
- `ocfs2_write_dquot()` inserts into the qtree if needed, writes the dquot at its offset, clears padding, swaps to disk endian, and writes the block.
- `ocfs2_delete_dquot()` removes a dquot reference, cleans empty leaves, updates free lists, and releases empty internal qtree blocks where possible.
- `ocfs2_read_dquot()` allocates a cached dquot, descends the qtree, finds the leaf entry by ID, sets `d_off`, copies/swap the disk dquot, and returns it.

Notable considerations:
- `ocfs2_read_global_quota_info()` returns early on `read_blk()` failure without freeing its allocated buffer, a small leak on error.
- Global quota qtree code is careful about free-list corruption but comments acknowledge some write failures can leave difficult states.

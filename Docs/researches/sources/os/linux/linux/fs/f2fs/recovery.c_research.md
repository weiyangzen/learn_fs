# File Research: sources/os/linux/linux/fs/f2fs/recovery.c

Implements F2FS roll-forward recovery for fsynced data after an unclean shutdown.

Recovery model:
- The file documents eight fsync/dentry-mark scenarios around checkpoint boundaries.
- Recovery scans warm-node segment chains starting at the current warm-node curseg next block.
- Recoverable nodes are identified by node footer checkpoint version/CRC via `is_recoverable_dnode()`.
- Fsync-marked dnodes identify inodes requiring replay.
- Dentry-marked inode nodes provide enough parent/name information to restore missing directory entries.

Key responsibilities:
- Determine whether there is space and roll-forward budget for recovery.
- Discover fsynced inode chains.
- Recover missing inode pages for new fsynced inodes.
- Restore inode metadata, dentries, inline xattrs, xattr nodes, inline data, and data block mappings.
- Avoid duplicate ownership of recovered data blocks by checking previous node references.
- Allocate new segments and write a checkpoint after successful replay.
- Provide lifecycle cache for `fsync_inode_entry`.

Important functions:
- `f2fs_space_for_roll_forward()`: checks block and optional rf-node limits.
- `add_fsync_inode()` / `del_fsync_inode()` / `destroy_fsync_dnodes()`: manage recovery inode list entries.
- `init_recovered_filename()`: reconstructs filename/hash state for recovered dentries, including encrypted+casefolded names.
- `recover_dentry()`: restores a dentry in the recorded parent directory, deleting conflicting entries when needed.
- `recover_quota_data()`: transfers UID/GID quota ownership changes before metadata replay.
- `recover_inode()`: restores mode, owner, size, timestamps, advise flags, F2FS flags, GC failures, inline flags, and project quota.
- `sanity_check_node_chain()`: uses Floyd-style cycle detection to prevent looping recovery node chains.
- `find_fsync_dnodes()`: scans recoverable node chain, builds the fsynced inode list, and optionally performs check-only detection.
- `check_index_in_prev_nodes()`: finds and truncates older references to a destination block before replaying a recovered mapping.
- `do_recover_data()`: recovers xattr/inline/data mappings for one recoverable node page.
- `recover_data()`: scans the recoverable node chain and applies inode, dentry, and data recovery for listed fsynced inodes.
- `f2fs_recover_fsync_data()`: top-level recovery flow under `cp_global_sem`.

Top-level recovery flow:
1. Take `cp_global_sem` to prevent checkpoint during recovery.
2. Scan for fsync dnodes with `find_fsync_dnodes()`.
3. In check-only mode, return whether recovery is needed.
4. Replay data and metadata with `recover_data()`.
5. Drop recovery meta pages and, on error, truncate node/meta mappings.
6. Check and fix zoned-device write pointer consistency.
7. Clear `SBI_POR_DOING` on success.
8. Drop directory inode references.
9. If replay happened, set `SBI_IS_RECOVERED` and write a recovery checkpoint.
10. Restore the original superblock read-only flag.

Consistency handling:
- Invalid block addresses, inconsistent summaries, looped node chains, and footer inconsistencies abort recovery.
- Dentry recovery handles encrypted filenames by logging `<encrypted>` instead of raw names.
- `check_index_in_prev_nodes()` uses segment summaries to locate previous owners of a block and truncate stale references.
- New inode recovery removes the recovered inode number from the free-NID cache to avoid reuse.

Dependencies:
- Depends heavily on node helpers from `node.h`/`node.c`, segment summaries and replacement helpers from `segment.h`, quota APIs, fscrypt/casefold directory helpers, and checkpoint/write-pointer logic from broader F2FS.

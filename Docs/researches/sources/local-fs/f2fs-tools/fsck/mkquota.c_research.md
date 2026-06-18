# File Research: sources/local-fs/f2fs-tools/fsck/mkquota.c

Purpose: builds and reconciles in-memory quota usage, then writes F2FS quota inode contents in VFS v1 quota format.

Key behavior:
- Uses dictionaries keyed by UID/GID/project ID to accumulate `struct dquot` usage records.
- `quota_write_inode()` creates a quota file handle for a quota type, writes all accumulated dquots through `commit_dquot()`, then closes the file and updates inode size.
- `quota_init_context()` allocates `quota_ctx`, initializes per-type dictionaries only for quota inodes present in the superblock, and tracks hard-linked inodes to avoid double counting.
- `quota_release_context()` frees quota dictionaries, linked-inode dictionary nodes, and context memory.
- `quota_data_add()`, `quota_data_sub()`, and `quota_data_inodes()` adjust current space and inode counts across all enabled quota dictionaries.
- `quota_add_inode_usage()` handles hard links and accounts inode block usage as `(i_blocks - 1) * F2FS_BLKSIZE` plus one inode count.
- `quota_compare_and_update()` opens an existing quota file, scans disk dquots, compares disk usage with measured usage, optionally preserves limits, and reports whether usage is inconsistent.
- `scan_dquots_callback()` marks seen entries, logs mismatches, copies limit fields when requested, and can copy usage from disk if enabled.

Important dependencies:
- Uses `dict_t` from `dict.h`.
- Uses generic quota IO from `quotaio.c`, V2 format operations from `quotaio_v2.c`, and qtree scanning from `quotaio_tree.c`.
- Called by fsck quota checks in `fsck.c` and by `do_fsck()` setup in `main.c`.

Risk notes:
- Fault injection for `FAULT_QUOTA` can force `quota_compare_and_update()` failure.
- Missing disk quota entries are treated as usage inconsistency.
- The code preserves limits only when requested, but always compares measured usage against on-disk usage.

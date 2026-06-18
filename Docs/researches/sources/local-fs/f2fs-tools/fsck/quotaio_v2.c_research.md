# File Research: sources/local-fs/f2fs-tools/fsck/quotaio_v2.c

Purpose: implements VFS v1 quota file format operations on top of the generic qtree layer.

Key behavior:
- Defines `quotafile_ops_2`, wiring check/init/new/write/read/commit/scan/report operations.
- Converts V2 revision 1 disk dquot blocks to/from `struct dquot`, including limits, current usage, grace timers, and ID.
- Uses a special all-zero entry with `dqb_itime = 1` marker for unused qtree entries when converting to disk.
- Converts disk quota info header fields into memory and back, including grace times, flags, qtree block count, free block, and free-entry heads.
- `v2_check_file()` reads the quota header, rejects wrong-endian magic, and verifies supported version.
- `v2_init_io()` initializes qtree entry size/ops, reads quota info, validates quota file size against discovered size-check state, repairs regular-file size mismatch by calling `f2fs_filesize_update()`, and checks qtree block/free-list bounds.
- `v2_new_io()` writes a new quota header and initializes default grace times and qtree metadata.
- `v2_write_info()` persists the in-memory quota info.
- `v2_commit_dquot()` deletes empty dquots or writes nonempty dquots through qtree.
- `v2_scan_dquots()` delegates to qtree scanning.
- `v2_report()` is intentionally unimplemented.

Important dependencies:
- Uses `quotaio.h`, `quotaio_v2.h`, `dqblk_v2.h`, and `quotaio_tree.h`.
- Relies on `f2fs_quota_size()` and `f2fs_filesize_update()` for F2FS quota inode sizing.

Risk notes:
- Size validation can mutate quota inode size during init when regular-file size metadata disagrees with observed block offsets.
- Format support is fixed to `QFMT_VFS_V1`/`V2_VERSION == 1`.

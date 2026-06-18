# File Research: sources/os/linux/linux/fs/quota/quota_v2.c

VFS quota v2 format support. This file validates v2 quota headers, reads/writes v2 file info, translates v2r0/v2r1 disk dquot records, and plugs the generic quota tree operations into the quota format interface.

Key responsibilities:
- Defines qtree conversion operations for:
  - v2r0: 32-bit limits/counters where applicable.
  - v2r1: 64-bit limits/counters.
- Reads and validates `struct v2_disk_dqheader` with `v2_read_header()` and `v2_check_quota_file()`.
- Reads v2 info header with `v2_read_file_info()`:
  - validates version against `QFMT_VFS_V0` / `QFMT_VFS_V1`,
  - allocates `struct qtree_mem_dqinfo`,
  - initializes tree block size, free lists, block count, depth, entry size, and conversion ops,
  - validates free block and free-entry pointers against file size.
- Writes info header with `v2_write_file_info()`.
- Converts v2r0/v2r1 records to/from `struct mem_dqblk`.
- Implements ID matching callbacks `v2r0_is_id()` and `v2r1_is_id()`.
- Wraps `quota_tree.c` operations:
  - `v2_read_dquot()`
  - `v2_write_dquot()`
  - `v2_release_dquot()`
  - `v2_get_next_id()`
- Frees format-private qtree state with `v2_free_file_info()`.
- Registers both `QFMT_VFS_V0` and `QFMT_VFS_V1`.

Important behavior:
- Uses an “escaped” all-zero entry by setting `dqb_itime = 1` when a real dquot would otherwise look unused to `qtree_entry_unused()`.
- v2r0 maximums are bounded by 32-bit quota-block values; v2r1 uses signed 63-bit limits in the generic quota core.
- Allocation of new dquot tree entries takes `dqio_sem` for write; overwriting existing entries takes it for read.
- All quota IO paths use `memalloc_nofs_save()`.

Research notes:
- `quota_tree.c` owns tree mechanics, while this file owns v2-specific header validation and disk payload conversion.

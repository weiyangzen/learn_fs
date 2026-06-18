# File Research: sources/local-fs/ocfs2-tools/fswreck/truncate_log.c

This file corrupts truncate log system inodes.

Key behavior:
- `create_truncate_log()` populates an empty truncate log with allocated cluster ranges, up to `tl_count`.
- `damage_truncate_log()` validates the inode has `OCFS2_DEALLOC_FL`, checks record availability for record-level corruptions, and mutates:
  - `tl_count`
  - `tl_used`
  - record start beyond filesystem cluster count
  - wrapped record start plus near-`UINT32_MAX` cluster count
  - record cluster count beyond filesystem size
- `get_truncate_log()` resolves the slot truncate log system inode.
- `mess_up_truncate_log_list()` damages header/list fields.
- `mess_up_truncate_log_rec()` creates ten truncate records, then damages selected records.

Integration notes:
- Uses endian conversion macros when creating records but direct assignment when corrupting fields.
- Slot default is slot 0 when caller passes `UINT16_MAX`.

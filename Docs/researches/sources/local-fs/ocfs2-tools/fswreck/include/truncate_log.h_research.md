# File Research: sources/local-fs/ocfs2-tools/fswreck/include/truncate_log.h

This header declares truncate log corruption helpers.

Exports:
- `mess_up_truncate_log_list()` for truncate log header/list fields.
- `mess_up_truncate_log_rec()` for individual truncate records.

Integration notes:
- Implemented in `truncate_log.c`.
- Used by `corrupt_truncate_log()`.

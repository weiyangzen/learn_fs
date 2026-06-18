# File Research: sources/local-fs/ocfs2-tools/fswreck/include/quota.h

This header declares `mess_up_quota()` for quota system-file corruption.

Integration notes:
- Implemented in `quota.c`.
- Dispatched from `corrupt_sys_file()` for quota fsck types.

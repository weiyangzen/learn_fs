# File Research: sources/local-fs/ocfs2-tools/fswreck/include/journal.h

This header declares `mess_up_journal()` for journal system-file corruption.

Integration notes:
- Implemented in `journal.c`.
- Dispatched from `corrupt_sys_file()` for journal-related fsck types.

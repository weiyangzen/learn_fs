# File Research: sources/local-fs/ocfs2-tools/fswreck/include/special.h

This header declares `mess_up_root()` for root/lost+found related special-file corruption.

Integration notes:
- Implemented in `special.c`.
- Used by `corrupt_file()` for root directory and lost+found prompt codes.

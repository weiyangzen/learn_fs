# File Research: sources/local-fs/xfsprogs/db/sb.h

Header for `xfs_db` superblock command and field support.

Key responsibilities:
- Declares superblock field tables.
- Declares `sb_init`, `sb_logcheck`, and `sb_size`.

Dependencies:
- Used by command initialization, field display, and log-safety paths.

Notable risks:
- Public declarations are small but central to `uuid` and label mutation safety.

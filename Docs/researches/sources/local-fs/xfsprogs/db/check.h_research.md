# File Research: sources/local-fs/xfsprogs/db/check.h

Purpose: minimal public declaration for the check command module.

Key contents:
- Declares `check_init(void)`.

Interactions:
- Included by `command.c`, which calls `check_init` from `init_commands`.
- Implemented by `check.c`.

Risks/notes:
- No include guard; this matches the simple style used by several small `xfs_db` headers in this area.

# File Research: sources/local-fs/xfsprogs/db/write.h

Header for `xfs_db` write support.

Key responsibilities:
- Declares `write_init`, `write_block`, `write_struct`, and `write_string`.

Dependencies:
- Used by the type registry and command initialization.

Notable risks:
- Exposes write entry points that assume global current-buffer/type state and expert-mode command gating elsewhere.

# File Research: sources/local-fs/xfsprogs/db/symlink.h

Header for CRC symlink block field support.

Key responsibilities:
- Declares symlink CRC field/header tables and `symlink_size`.

Dependencies:
- Used by `type.c` and symlink field-printing paths.

Notable risks:
- Must remain aligned with ondisk remote symlink header layout.

# File Research: sources/local-fs/xfsprogs/db/type.h

Core type-system header for `xfs_db`.

Key responsibilities:
- Defines `typnm_t` enum values for all recognized object types.
- Defines action constants `DB_READ`, `DB_WRITE`, and `DB_FUZZ`.
- Defines `typ_t`, including type name, action dispatcher, field table, buffer ops, CRC offset policy, and CRC setter.
- Declares type registry globals and handler functions.

Dependencies:
- Shared by type registry, print/write/fuzz paths, and field modules.

Notable risks:
- Enum order is a contract with `type.c` tables.

# File Research: sources/local-fs/xfsprogs/db/dquot.h

Purpose: public declarations for quota field metadata and command/CRC helpers.

Key contents:
- Declares `disk_dquot_flds`, `dqblk_flds`, and `dqblk_hfld`.
- Declares `xfs_dquot_set_crc`.
- Declares `dquot_init`.

Interactions:
- Included by `field.c`, `dquot.c`, and command initialization.

Risks/notes:
- Uses `struct field` declarations without including the full field definition, relying on consumers to include appropriate headers.

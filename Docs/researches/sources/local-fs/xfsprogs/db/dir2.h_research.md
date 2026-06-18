# File Research: sources/local-fs/xfsprogs/db/dir2.h

Purpose: declarations shared by directory v2/v3 field modules.

Key contents:
- Declares common field tables for block tails, data free entries, data unions, leaf tails, leaf entries, and DA node entries.
- Declares v2-specific field tables for directory root, data headers, free headers, leaf headers, DA block info, and DA node headers.
- Declares v3-specific field tables for directory root, block headers, data headers, free headers, leaf headers, data unions, DA3 block info, and DA3 node headers.
- Provides inline `xfs_dir2_sf_inumberp` to locate the shortform entry inumber payload.
- Declares size helpers `dir2_data_union_size` and `dir2_size`.
- Declares `xfs_dir3_set_crc` and `xfs_dir3_db_buf_ops`.

Interactions:
- Used by `dir2.c`, `dir2sf.c`, `field.c`, and code that needs directory CRC/verifier support.

Risks/notes:
- Exposes field-table symbols rather than opaque accessors, matching the `xfs_db` field registry design.

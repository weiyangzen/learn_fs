# File Research: sources/local-fs/xfsprogs/db/dir2sf.c

Purpose: defines field metadata and size/offset callbacks for shortform XFS directory v2/v3 data stored inside an inode fork.

Key behavior:
- Defines `dir2sf_flds` with header and entry list fields.
- Defines `dir2_inou_flds`, exposing either 4-byte or 8-byte inode fields depending on the shortform header `i8count`.
- Defines `dir2_sf_hdr_flds` for `count`, `i8count`, and `parent`.
- Defines `dir2_sf_entry_flds` for namelen, offset, name, and inumber.
- `dir2_sf_entry_size`, `dir2_sf_hdr_size`, `dir2sf_size`, list count, and list offset callbacks walk variable-length shortform entries with libxfs helpers.
- Defines v3 shortform variants `dir3sf_flds` and `dir3_sf_entry_flds`; v3 entries include filetype and place the inumber after the filetype byte.
- `dir2_inou_size` returns either 32-bit or 64-bit inode-number size based on `i8count`.

Interactions:
- Field types are registered by `field.c`.
- Uses `xfs_dir2_sf_inumberp` from `dir2.h` and libxfs shortform directory helpers.
- Used by inode/directory print paths and by any command that traverses shortform directory fields.

Risks/notes:
- Size and offset calculations assume the shortform entry list is structurally walkable; corrupt counts or lengths can affect field traversal.

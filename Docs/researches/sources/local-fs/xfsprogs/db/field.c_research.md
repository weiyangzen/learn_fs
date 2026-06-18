# File Research: sources/local-fs/xfsprogs/db/field.c

Purpose: central field-type registry for `xfs_db` and helper functions for field offsets, counts, lookup, and sizes.

Key behavior:
- Defines `parent_flds` for XFS parent records.
- Defines `ftattrtab`, mapping every `fldt_t` field type to:
  - User-visible type name.
  - Print function.
  - Print format.
  - Fixed or dynamic bit size.
  - Field arguments such as null/zero skipping, signedness, dynamic sizing, and empty-union allowance.
  - Optional address navigation callback.
  - Optional subfield table.
- Registers field types for AG headers, AGFL, AGI, attributes, bmap btrees, bmbt roots, free-space btrees, rmap/refcount btrees, realtime rmap/refcount roots, CRCs, dinodes, directory v2/v3 and shortform layouts, quota blocks, realtime bitmap/summary fields, superblocks, timestamps, UUIDs, parent records, and scalar integer/string forms.
- `bitoffset` resolves a field’s bit offset, handling static offsets, dynamic offset callbacks, and static array indexing with optional one-based indexing.
- `fcount` resolves static or dynamic field counts.
- `findfield` locates a named field with nonzero count.
- `fsize` resolves static or dynamic field bit size.

Interactions:
- Pulls field tables from many modules: AGF/AGFL/AGI, sb, attr, dir2, dir2sf, dquot, inode, btree, symlink, realtime group, and others.
- Used by `print`, `flist`, `crc`, and navigation code to parse and display arbitrary metadata structures.

Risks/notes:
- This file is a central coupling point: adding any new on-disk metadata field type requires updating `fldt_t` and `ftattrtab` consistently.
- Dynamic size/count/offset callbacks must tolerate corrupt on-disk data because field traversal is often used for debugging damaged metadata.

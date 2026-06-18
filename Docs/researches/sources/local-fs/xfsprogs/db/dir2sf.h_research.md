# File Research: sources/local-fs/xfsprogs/db/dir2sf.h

Purpose: public declarations for shortform directory field tables and sizing callbacks.

Key contents:
- Declares v2 field tables: `dir2sf_flds`, `dir2_inou_flds`, `dir2_sf_hdr_flds`, `dir2_sf_entry_flds`.
- Declares v3 field tables: `dir3sf_flds`, `dir3_sf_entry_flds`.
- Declares size helpers for the whole shortform directory, inode union, shortform entry, and shortform header.

Interactions:
- Included by `field.c` and `dir2sf.c`.

Risks/notes:
- Header is field-registry oriented; it does not provide validation helpers.

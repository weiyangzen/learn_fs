# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/meta.c

This file defines metadata schemas, symbolic tables, lookup helpers, formatting, and assignment for GFS2 on-disk structures.

Major data:
- Symbol tables for metatypes, metaformats, dinode flags, log-header flags, and log descriptor types.
- `lgfs2_metadata[]`: schemas for superblock, rindex, rgrp, rgrp bitmap, dinode, indirect, leaf, journal data, log header/descriptor/block, EA blocks, quota change, dirent, EA header, inum range, statfs change, data, and free blocks.
- Per-field metadata: name, offset, length, flags, pointer target types, symbol tables.

Public APIs:
- `lgfs2_find_mfield_name()`
- `lgfs2_find_mtype()`
- `lgfs2_find_mtype_name()`
- `lgfs2_field_str()`
- `lgfs2_flag_sym_value()`
- `lgfs2_field_assign()`

Integration role:
- Drives `gfs2l`, field rendering, field assignment, metadata inspection, and structure listing.
- Uses kernel on-disk structure definitions for offsets and sizes.

Risk notes:
- Schema tables must match `linux/gfs2_ondisk.h` exactly.
- `lgfs2_find_mtype()` returns first matching `mh_type`; multiple historical GFS/GFS2 entries in the enum would require care.
- `lgfs2_field_assign()` reads `uint64_t num = *(uint64_t *)val` before checking UUID/string flags, so callers must pass sufficiently aligned/sized memory for numeric paths.
- String field assignment rejects strings that fill the full field length.

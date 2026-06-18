# File Research: sources/os/linux/linux/fs/udf/udfdecl.h

Purpose: primary internal declaration header for UDF.

Key contents:
- Includes ECMA-167, OSTA UDF, endian helpers, superblock, and inode private headers.
- Defines logging macros, extent length/flag masks, invalid ID, name limits, and default preallocation.
- `udf_file_entry_alloc_offset()` computes allocation descriptor offset for unallocated space entries, extended file entries, and normal file entries while accounting for EA length.
- `udf_ext0_offset()` returns inline data offset for AD-in-ICB files.
- Declares VFS operation tables, export operations, core inode/file/directory/allocation/truncate/partition/unicode/time helpers.
- Defines `struct udf_fileident_iter` for directory iteration and descriptor writing.
- Defines descriptor scan helper structs used by `super.c`.
- Provides `udf_updated_lvid()` helper and `udf_get_lb_pblock()` logical block translation wrapper.

Integration:
- This is the connective header used by all UDF `.c` files in this group.
- Couples UDF modules through explicit prototypes and shared inline layout helpers.

Risks and invariants:
- Allocation descriptor offsets are layout-critical; mistakes corrupt file entries.
- Directory iterator state supports entries spanning buffers, so users must release it correctly.
- `udf_updated_lvid()` assumes an open LVID buffer and marks the superblock LVID dirty.

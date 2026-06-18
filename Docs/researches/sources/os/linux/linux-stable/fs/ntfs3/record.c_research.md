# File Research: sources/os/linux/linux-stable/fs/ntfs3/record.c

Purpose: Handles individual MFT record lifecycle, attribute enumeration/validation, attribute insertion/removal/resizing, and repacking of nonresident runlists inside a record.

Key responsibilities:
- Allocates, initializes, reads, writes, formats, and frees `struct mft_inode` through `mi_get()`, `mi_put()`, `mi_init()`, `mi_read()`, `mi_write()`, and `mi_format_new()`.
- Enumerates and validates attributes in an MFT record with `mi_enum_attr()`.
- Finds attributes by type, name, and optional id via `mi_find_attr()`.
- Inserts ordered attributes with `mi_insert_attr()`, assigning ids through `mi_new_attt_id()`.
- Removes attributes with `mi_remove_attr()`, including hard-link decrement handling for indexed file-name attributes.
- Resizes resident attributes and shifts record tail data with `mi_resize_attr()`.
- Rebuilds packed mapping pairs in-place with `mi_pack_runs()`.

Important invariants:
- `mi_read()` accepts fixup failures by marking the record dirty, but rejects wrong `rec->total`.
- `mi_enum_attr()` is the key corruption boundary for record contents: it checks used/total bounds, alignment, ordered attribute types, resident/nonresident header sizes, name/data/run offsets, VCN ordering, valid/data/allocated sizes, compression/sparse total size, cluster alignment, and volume bounds.
- Attribute order is by type and then name collation using the volume upcase table.
- Duplicate non-indexed attributes of the same type/name are rejected during insertion.
- Writes to records below `sbi->mft.recs_mirr` set `NTFS_FLAGS_MFTMIRR` so the mirror can be updated.

Dependencies:
- Uses low-level metadata I/O helpers from `fsntfs.c`.
- Uses run packing from `run.c`.
- Uses name collation from `upcase.c`.
- Uses NTFS inode dirty/error helpers declared in `ntfs_fs.h`.

Risk notes:
- Corruption detected during enumeration calls `_ntfs_bad_inode()` and returns `NULL`, which can look like normal end-of-enumeration to some callers unless they also check inode state.
- `mi_pack_runs()` temporarily opens a maximum gap in the record and must restore tail data on failure.
- `mi_resize_attr()` adjusts `res.data_size` for resident attributes only; nonresident size changes are handled elsewhere.

# File Research: sources/os/linux/linux/fs/ntfs3/record.c

## Role

Implements low-level MFT record lifecycle and in-record attribute manipulation. It allocates, reads, validates, formats, writes, inserts, removes, resizes, and repacks attributes inside one `struct mft_inode`.

## Major Functions

- `compare_attr()`: orders attributes by type and name using the upcase table.
- `mi_new_attt_id()`: allocates an unused attribute ID, reusing gaps when the record's next ID reaches high values.
- `mi_get()` / `mi_put()` / `mi_init()` / `mi_clear()`:
  - Allocate, initialize, read, and free `mft_inode` instances.
- `mi_read()`:
  - Reads one MFT record through `$MFT` run mappings.
  - Handles missing loaded runs by loading more `$MFT` runs and retrying.
  - Treats fixup failure specially by marking the record dirty but allowing continuation.
  - Verifies `rec->total` matches `sbi->record_size`.
- `mi_enum_attr()`:
  - Enumerates attributes in an MFT record and performs extensive bounds/format validation.
  - Validates used/total boundaries, alignment, attribute ordering, resident/nonresident sizes, VCN ranges, run offsets, names, alloc/data/valid/total sizes, compression/sparse rules, and volume bounds.
  - Marks the inode bad if corruption is detected.
- `mi_find_attr()`:
  - Finds an attribute by type, name, and optional ID.
- `mi_write()`:
  - Writes dirty MFT record buffers and flags `$MFTMirr` updates for mirrored records.
- `mi_format_new()`:
  - Initializes a new/reused MFT record from `sbi->new_rec`, preserving or generating sequence numbers.
- `mi_insert_attr()`:
  - Inserts a new attribute in sorted position, assigns an ID, shifts the record tail, and marks dirty.
- `mi_remove_attr()`:
  - Removes an attribute, shifts the tail, updates hard-link count for indexed file-name attributes, and marks dirty.
- `mi_resize_attr()`:
  - Grows or shrinks an attribute in-place by aligned bytes, shifting trailing attributes.
- `mi_pack_runs()`:
  - Re-packs a nonresident attribute's mapping pairs into available record space, preserving the record if packing fails.

## Important Invariants

- MFT records must have `rec->total == sbi->record_size` after reading.
- Attribute enumeration enforces increasing attribute type order.
- Attribute sizes and offsets must be 8-byte aligned and contained within `rec->used`.
- Resident data must fit between `data_off` and attribute size.
- Nonresident attributes must have valid `svcn <= evcn + 1`, `valid_size <= data_size <= alloc_size`, cluster-aligned allocation sizes, and acceptable `total_size` rules for sparse/compressed streams.
- Insertion/removal/resizing depends on `memmove` over validated in-record boundaries.

## Dependencies

- Uses `ntfs_read_bh`, `ntfs_write_bh`, `ntfs_get_bh`, `attr_load_runs_vcn`, and `run_pack`.
- Consumes on-disk structures from `ntfs.h` and in-memory state from `ntfs_fs.h`.
- Cooperates with `$MFT` run locking during reads and formatting.

## Notes For Future Work

- `mi_enum_attr()` is a central corruption boundary. Bugs here can turn malformed disk bytes into unsafe pointer arithmetic elsewhere.
- `mi_read()` allows `-E_NTFS_FIXUP` to proceed with `mi->dirty = true`; this behavior should remain paired with a clear understanding of NTFS fixup recovery semantics.
- Attribute insertion rejects duplicate non-indexed attributes with same type/name, but allows indexed duplicates.

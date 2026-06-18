# File Research: sources/os/linux/linux-stable/fs/ntfs3/ntfs.h

Purpose: Defines NTFS3 on-disk ABI structures, constants, little-endian enums, and small layout/access helpers used across the driver.

Key contents:
- NTFS core constants: name length/link limits, LZNT compression unit sizes, special LCN markers, predefined MFT record numbers, attribute type values, and DOS/NTFS file attribute flags.
- Packed on-disk structures for the boot sector, MFT record header/body, resident and nonresident attributes, standard information, attribute-list entries, file-name attributes, directory index entries, index headers/buffers/roots, `$Volume`, `$AttrDef`, object-id, quota, security, reparse, EA, ACL, SID, and relative security descriptor data.
- Reparse-point constants and structures for mount points, symlinks, WOF/system compression, cloud tags, and generic reparse buffers.
- Inline helpers for MFT references, record state, attribute size/name/data pointers, directory-entry VBN access, index-entry traversal, and small filename/index utilities.

Important invariants:
- This file is layout sensitive; it uses `static_assert()` heavily to pin exact sizes and offsets for structures consumed from disk.
- `CLST` is 32-bit by default and 64-bit only with `CONFIG_NTFS3_64BIT_CLUSTER`; sparse/resident/compressed/EOF/delalloc sentinel LCNs depend on that type.
- Attribute flags and type enums are stored as little-endian values, so helpers generally convert before arithmetic and comparisons.
- Resident data helpers validate size/offset only in `resident_data_ex()`; raw `resident_data()` and `attr_run()` assume prior validation.
- Index-entry helpers trust the entry-size field except where `hdr_first_de()` and `hdr_next_de()` check header bounds.

Dependencies:
- Included by almost every NTFS3 implementation file through `ntfs_fs.h`.
- Relies on Linux endian/types/build assertions and local pointer helpers from `debug.h`.

Risk notes:
- Any change to fields, packing, or constants can break disk compatibility.
- The `le_cmp()` helper appears intended to compare attribute-list entry names with attributes, but its current `memcmp()` is gated by `!le->name_len`; callers should be checked carefully before relying on it for non-empty names.

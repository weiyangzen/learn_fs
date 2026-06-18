# File Research: sources/local-fs/linux-apfs-rw/xfield.c

This file implements helpers for APFS extended fields stored inside inode and dentry records. Extended fields are represented as an `apfs_xf_blob` header, followed by fixed-size metadata entries, followed by padded value data.

Exports:
- `apfs_find_xfield(u8 *xfields, int len, u8 xtype, char **xval)` locates the value for one xfield type and returns its padded length, or `0` if absent/corrupt.
- `apfs_init_xfields(u8 *buffer, int buflen)` initializes an empty xfield collection.
- `apfs_insert_xfield(u8 *buffer, int buflen, const struct apfs_x_field *xkey, const void *xval)` inserts or replaces an xfield in an in-memory buffer and returns the new collection length.

Core behavior:
- `apfs_find_xfield()` validates the blob header and metadata array fit inside the supplied length, walks each xfield entry, rounds each value length up to 8 bytes, and returns a pointer into the value area for the matching type.
- `apfs_init_xfields()` writes zero count and used-data fields.
- `apfs_insert_xfield()` supports both replacement and insertion. Replacement updates metadata, resizes the padded value, shifts trailing value bytes with `memmove()`, and updates used-data. Insertion creates a new metadata entry, shifts existing payload to make room, writes value bytes, zero-fills padding, and updates blob counters.

Integration points:
- Directory code uses these helpers for dentry sibling IDs and related APFS directory metadata.
- Inode code uses them for name, device number, sparse-byte count, and other inode extended fields.
- Prototypes live in `apfs.h`.

Error and corruption handling:
- The helpers return `0` for missing fields, invalid/corrupt layouts, or insufficient buffer capacity, so callers must distinguish “not found” from “bad collection” by context.
- Value sizes are always padded to 8 bytes, matching APFS xfield layout expectations.
- Callers must validate expected structure sizes before casting `*xval`, as noted in the function comment.

Risks and watchpoints:
- `apfs_insert_xfield()` mutates the buffer before all final capacity checks complete in some paths; current callers appear to operate on prepared in-memory construction buffers, but failed insertions should not be assumed to leave the buffer untouched.
- The API returns padded value length, not logical `x_size`, which is correct for traversal but important for typed consumers.

# File Research: sources/local-fs/squashfs-tools/squashfs-tools/read_xattrs.c

Shared xattr reader for mksquashfs append and unsquashfs extraction. It reads the xattr id table, validates id counts and index byte layout, decompresses xattr id metadata and xattr value metadata, and stores a hash mapping from compressed metadata block start to uncompressed in-memory offset.

`prefix_table` maps Squashfs xattr prefix ids to `user.`, `trusted.`, and `security.`. `read_xattr_entry()` reconstructs full names and rejects unknown prefixes.

`get_xattr()` walks an xattr id entry, bounds-checking every metadata access, supports out-of-line values, returns known xattrs, and marks `failed` when unknown prefix types are skipped. Corruption returns `NULL` with a fatal error message.

`free_xattr()` frees reconstructed names and list storage.

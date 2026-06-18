# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_attr_sf.h

## Purpose

`xfs_attr_sf.h` defines small helper types and inline accessors for XFS shortform extended attributes, which are stored packed inside the inode attr fork.

## Main Definition

`xfs_attr_sf_sort_t` is an in-memory sorting record used when attr listing must return entries in hash order. It records original entry number, name length, value length, flags, computed hash, and pointers into the shortform buffer for name and value.

## Inline Helpers

- `XFS_ATTR_SF_ENTSIZE_MAX` is the maximum name/value byte count representable by the one-byte shortform length fields.
- `xfs_attr_sf_entsize_byname` computes packed storage for a name/value length pair.
- `xfs_attr_sf_entsize` computes packed storage for an existing entry.
- `xfs_attr_sf_firstentry` returns the first entry after the shortform header.
- `xfs_attr_sf_nextentry` advances to the next variable-length entry.
- `xfs_attr_sf_endptr` returns the byte after the last entry using the big-endian total size field.

## Invariants

Shortform entry traversal depends entirely on trusted `namelen`, `valuelen`, and `totsize` after verification. Callers must verify raw forks before iterating untrusted on-disk data. Lengths are one byte, so larger attrs must use leaf/remote formats.

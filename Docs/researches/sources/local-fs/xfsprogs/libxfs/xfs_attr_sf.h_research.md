# File Research: sources/local-fs/xfsprogs/libxfs/xfs_attr_sf.h

## Purpose

`xfs_attr_sf.h` defines small inline helpers and a sort record for XFS shortform extended attributes stored inside the inode attr fork.

## Key Contents

`xfs_attr_sf_sort_t` captures entry number, name length, value length, flags, hash, name pointer, and value pointer for sorting shortform attrs into hash order for listing. `XFS_ATTR_SF_ENTSIZE_MAX` reflects the maximum one-byte name/value length component.

Inline helpers compute entry sizes by lengths or by entry, find the first entry after the shortform header, advance to the next variable-length entry, and find the end pointer using the big-endian `totsize` field.

## Dependencies and Risks

The helpers assume the caller has already verified the packed shortform buffer boundaries. Miscomputed `namelen`, `valuelen`, or `totsize` would make pointer iteration unsafe, so this header is paired with the shortform verifier in `xfs_attr_leaf.c`.

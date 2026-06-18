# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.h

## Role

Shared declarations for `ntfscluster.c`.

## Main Definitions

- `enum action` names supported command actions: info, cluster, sector, inode, file, last, and error.
- `struct options` stores parsed CLI state, target device, range, filename, inode, and verbosity/force flags.
- `struct match` stores inode, LCN, attribute type/name, and name length for cluster-match tracking.

## Dependencies

Includes NTFS basic types and layout definitions.

## Research Notes

The header is local to the `ntfscluster` utility and has no cross-tool API surface.

# File Research: sources/local-fs/xfsprogs/repair/phase6.c

## Role

`phase6.c` implements xfs_repair phase 6: checking inode connectivity, validating and repairing directory contents, recreating required root/realtime/quota metadata inodes, moving disconnected inodes to `lost+found`, and feeding expected parent-pointer records to `pptr.c`.

## Core Flow

1. Initializes parent pointer tracking.
2. Tears down phase 5 extent state and adds inode extra data.
3. Reinitializes missing root and metadata-root directories.
4. Rebuilds realtime bitmap/summary/rmap/refcount metadata, either sb-rooted or metadata-directory rooted.
5. Recreates/relinks quota metadata files on metadir filesystems.
6. Marks standalone metadata inodes as reached.
7. Traverses all directory inodes using inode prefetch.
8. Rebuilds directories whose `..` entries had to be inferred.
9. Moves unreached inodes into `lost+found`.
10. Cross-checks and repairs parent pointer xattrs.

## Directory Repair

- Longform directories are validated by scanning data blocks, leaf blocks, node blocks, and free-space blocks.
- Shortform directories are checked in-place and can remove junk entries by compacting the local data fork.
- The directory hash table tracks entries by name and address to detect duplicate names, missing leaf entries, duplicate leaf entries, bad hash values, and bad stale counts.
- Bad entries are marked by overwriting the name with `/`, then the directory can be rebuilt from salvaged entries.
- Ftype mismatches are repaired when the filesystem supports directory file types.
- Missing `.` and selected missing `..` entries are recreated or scheduled for rebuild.

## Connectivity Repair

- Directory traversal updates reached/reference counts in the in-core inode tree.
- Directories already reached through another parent are treated as inconsistent and their duplicate entry is junked.
- Disconnected inodes are linked into `lost+found`; directories have `..` updated to point there.
- Metadata inode contents are truncated before relocation to avoid exposing metadata payloads through `lost+found`.

## Dependencies

This file depends on libxfs directory, inode, transaction, parent pointer, realtime, quota, and metadir APIs; repair inode trees; prefetch; progress; parent pointer tracking; quota skip handling; and rmap/realtime rebuild helpers.

## Risk Areas

- Directory salvage must balance preserving recoverable entries against avoiding links to free, missing, metadata/regular mismatched, or already-connected inodes.
- Parent pointer correctness depends on every surviving directory entry being recorded through `add_parent_ptr()`.
- Rebuilding metadata directories and quota/realtime metadata changes inode reachability and quota-check behavior.

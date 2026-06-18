# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscp.c

## Role

Implements `ntfscp`, a write utility that copies a local file into an NTFS file or attribute, creating the destination when needed and optionally minimizing fragmentation.

## Main Areas

- `parse_options()` handles device/source/destination, attribute type/name, inode mode, timestamp copy, no-action, force, and verbosity.
- Signal handling records SIGINT/SIGTERM so the copy loop can abort cleanly.
- Minimal-fragmentation allocation scans `$Bitmap`, selects large free runs, sorts them by LCN, assigns a custom runlist, updates mapping pairs, and marks clusters allocated.
- `ntfs_new_file()` wraps Unicode conversion and `ntfs_create()` for regular file creation.
- `main()` mounts the volume, resolves or creates the destination, opens/adds the target attribute, resizes it, writes data with `ntfs_attr_pwrite()`, closes compressed attributes with `ntfs_attr_pclose()`, optionally updates timestamps, and syncs by closing the inode.

## Dependencies

Uses libntfs-3g volume, directory/pathname, inode creation, attribute truncate/write, bitmap, runlist, timestamp, logging, and utility APIs.

## Important Behavior

`--min-fragments` is disabled for compressed attributes. Existing attributes are truncated to zero before minimal-fragmentation preallocation. No-action mounts read-only and skips actual runlist assignment/writes where relevant.

If the destination path resolves to a directory and destination is not inode mode, the source basename is copied into that directory, overwriting an existing same-name file when found. Inode mode treats the destination argument as an MFT reference and can write directly to that inode’s selected attribute.

## Research Notes

The custom preallocator is the highest-risk part: it mutates `$Bitmap`, runlists, mapping pairs, and attribute/inode size fields directly. The normal copy path relies more on libntfs-3g truncate/write helpers.

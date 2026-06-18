# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.c

## Role

Implements `ntfscluster`, a read-only inspection utility that finds the owner of a cluster/sector range or dumps runlists for a file/inode.

## Main Functions

- `parse_options()` selects exactly one action: info, cluster range, sector range, inode, filename, or last.
- `info()` walks MFT records and non-resident attributes to compute metadata, user-data, and free-space statistics.
- `dump_file()` prints all attributes of an inode and runlists for non-resident attributes.
- `print_match()` is the `cluster_find()` callback that prints inode and attribute names for range matches.
- `find_last()` is a callback for locating the file with the highest referenced LCN.
- `main()` mounts the volume read-only, dispatches the selected action, and unmounts.

## Dependencies

Uses `ntfscluster.h`, libntfs-3g volume, directory/pathname, attribute, cluster, runlist, MFT search, and logging helpers.

## Important Behavior

Sector ranges are converted to cluster ranges by shifting with `cluster_size_bits - sector_size_bits`. `--force` maps to `NTFS_MNT_RECOVER`; otherwise the volume is mounted read-only without recovery. File lookup uses `ntfs_pathname_to_inode()` and Windows builds translate paths first.

## Research Notes

The tool is a thin front end over libntfs-3g’s MFT and cluster scanning helpers. Its output is diagnostic and it does not modify the filesystem.

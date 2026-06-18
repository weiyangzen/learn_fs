# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscluster.8.in

## Role

Manual page for `ntfscluster`, describing it as a tool for identifying files occupying a specified sector or cluster range on an NTFS volume.

## Documented Interface

Documents `--cluster`, `--sector`, `--inode`, `--filename`, `--force`, `--quiet`, `--verbose`, `--version`, and `--help`. It explains range-based cluster/sector lookup and file/inode inspection.

## Important Behavior

The manpage says `info` mode is not implemented, but the current `ntfscluster.c` does implement `info()` and prints volume, MFT, free-space, user-data, and metadata statistics.

## Research Notes

The page is useful for command-line semantics but slightly stale relative to implementation.

# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfscp.8.in

## Role

Manual page for `ntfscp`, which copies a host file into an NTFS volume.

## Documented Interface

Documents destination by path or inode, optional attribute type/name, `--min-fragments`, `--no-action`, `--force`, `--timestamp`, quiet/verbose, and version/help options. It also explains NTFS named data streams.

## Important Behavior

The manpage notes the unusual case of writing an unnamed data attribute to a directory when the destination is specified by inode number.

## Research Notes

The documentation aligns with the implementation’s file creation, overwrite, named stream, inode-target, and minimal-fragmentation features.

# File Research: sources/local-fs/btrfs-progs/cmds/inspect.c

## Purpose

Implements the `btrfs inspect-internal` command group. This file exposes developer/admin inspection helpers for resolving inode and logical addresses, mapping subvolume IDs, computing minimum device shrink sizes, enumerating chunks, and checking swapfile physical offsets.

## Commands Implemented

- `inode-resolve`: maps an inode number to filesystem paths using `BTRFS_IOC_INO_PATHS`.
- `logical-resolve`: maps a logical address to inode/root/offset triples or resolved paths using `BTRFS_IOC_LOGICAL_INO` / `BTRFS_IOC_LOGICAL_INO_V2`.
- `subvolid-resolve`: resolves a subvolume ID to a path with `btrfs_subvolid_resolve`.
- `rootid`: returns the containing subvolume tree ID for a path via `lookup_path_rootid`.
- `min-dev-size`: estimates the minimum shrinkable size for a device by reading device extents and modeling relocation scratch space.
- `list-chunks`: lists physical/logical chunk mappings and usage, with multi-key sorting and unit formatting.
- `map-swapfile`: verifies a file is suitable as a Btrfs swapfile and maps its first physical block/resume offset.

## Key Helpers and Data Structures

- `__ino_to_path_fd()` wraps inode-to-path ioctl results and prints each returned path.
- `struct dev_extent_elem` stores device extent/hole ranges for minimum device size estimation.
- `adjust_dev_min_size()` accounts for extents beyond the provisional minimum size, usable holes, superblock mirror locations, relocation scratch space, and possible system chunk allocation.
- `struct list_chunks_entry` records one stripe/chunk row: device ID, physical start, logical start, length, flags, usage, and numbering.
- `print_list_chunks()` builds a table with columns for device, physical/logical numbering, type/profile, offsets, length, and usage.
- `read_chunk_tree()`, `find_chunk()`, and `map_physical_start()` support swapfile mapping by reconstructing chunk-to-stripe layout and file extent placement.

## External Interfaces

The file depends heavily on kernel Btrfs ioctls and tree-search helpers:

- `BTRFS_IOC_INO_PATHS`
- `BTRFS_IOC_LOGICAL_INO`
- `BTRFS_IOC_LOGICAL_INO_V2`
- `BTRFS_IOC_TREE_SEARCH`
- `BTRFS_IOC_INO_LOOKUP`
- `FS_IOC_GETFLAGS`

It also uses shared btrfs-progs helpers for mount parsing, subvolume ID resolution, path/root lookup, unit formatting, table output, sorting, and open handling.

## Important Behavior

- `logical-resolve` switches to the v2 ioctl when the buffer exceeds 64 KiB or when `--ignore-offsets` is requested.
- `logical-resolve` attempts to map resolved root IDs back to currently mounted subvolumes; if a referenced subvolume is not mounted, it reports that path resolution cannot continue for that inode.
- `min-dev-size` is intentionally conservative because relocation can require temporary scratch space and may allocate a system chunk.
- `list-chunks` computes logical numbering per device and physical numbering after sorting by device and physical offset.
- `map-swapfile` rejects non-regular files, non-Btrfs files, non-NOCOW files, compressed files, holes, inline extents, encrypted/encoded extents, unsupported block group profiles, and files spanning multiple devices.

## Notes

This file is a read-only inspection and validation surface except for opening files/directories and querying kernel state. It is central to low-level diagnostics and exposes details that normal user-facing commands hide.

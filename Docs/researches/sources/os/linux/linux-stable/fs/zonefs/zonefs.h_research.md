# File Research: sources/os/linux/linux-stable/fs/zonefs/zonefs.h

## Purpose

Defines the primary zonefs in-memory and on-disk structures, constants, feature flags, mount options, helper functions, and cross-file declarations.

## Main Responsibilities

- Defines zone types, flags, and type helpers.
- Defines per-zone, per-zone-group, per-inode, on-disk superblock, and per-superblock structures.
- Defines feature flags for conventional aggregation, UID, GID, and permissions.
- Defines mount option flags for error handling and explicit zone opens.
- Provides inline helpers for inode/private zone access and I/O error locking.
- Declares super, file, and sysfs interfaces.

## Important Invariants

- Zonefs file names need only fit group names and decimal zone numbers.
- Sequential zones include both required and preferred sequential zone block types.
- `i_truncate_mutex` serializes truncate, iomap begin, private zone state, write refcount, and sequential size updates.
- Offline/read-only state is tracked in zone flags and reflected into inode mode.
- On-disk superblock size is fixed at 4096 bytes.
- Defined feature bits are strictly enumerated.

## Dependencies

Uses Linux VFS, magic numbers, UUIDs, mutex/rwsem/kobject APIs, block zone definitions, and iomap-facing file declarations.

## Research Notes

This header is the architectural map for zonefs: zone files are synthetic inodes backed directly by block-device zone geometry and write-pointer state.

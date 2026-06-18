# File Research: sources/os/linux/linux/fs/zonefs/super.c

## Purpose

Implements zonefs mount, superblock parsing, zone discovery, inode/directory construction, statfs, mount options, error recovery, and module registration.

## Main Responsibilities

- Registers zonefs filesystem type and inode cache.
- Parses mount options: `errors=` and `explicit-open`.
- Reads and validates the zonefs on-disk superblock, CRC, features, UID/GID, permissions, and UUID.
- Reports block-device zones and builds conventional/sequential zone groups.
- Creates root, zone group directory, and zone file inodes.
- Aggregates contiguous conventional zones when the feature is enabled.
- Tracks used blocks and active/open sequential zone counts.
- Executes zone management operations.
- Handles runtime I/O errors by re-reporting zone condition and updating inode mode/size/write pointer.
- Implements lookup/readdir for the generated namespace.
- Handles remount option updates and unmount cleanup.

## Important Invariants

- zonefs can mount only zoned block devices.
- First zone contains the zonefs superblock and is not exposed as a file.
- File names are decimal zone-group indices without leading zeroes.
- Sequential zone active/open accounting excludes conventional zones.
- Offline zones become unreadable/unwritable immutable files.
- Read-only zones become immutable and lose write permissions.
- `explicit-open` is ignored if the device reports no open or active zone limits.
- The filesystem block size is set to device zone write granularity.

## Dependencies

Uses Linux fs_context, block zoned APIs, CRC32, inode cache, dentry/inode helpers, sysfs registration, iomap-facing file ops, and zonefs tracepoints.

## Research Notes

This file synthesizes a filesystem namespace from block device zone state. Its most important runtime behavior is error recovery, where zone condition and write pointer are re-read to prevent exposing invalid data.

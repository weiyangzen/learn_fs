# File Research: sources/local-fs/btrfs-progs/cmds/rescue-super-recover.c

## Purpose

Implements `btrfs rescue super-recover` backend. It scans all devices and superblock mirror locations, classifies valid current-generation superblocks as good and invalid/outdated ones as bad, then rewrites all superblock copies from a good copy after user confirmation.

## Main API

- `int btrfs_recover_superblocks(const char *dname, int yes)`

## Control Flow

1. Opens the provided device and scans filesystem devices in recovery mode.
2. `read_fs_supers()` iterates all devices and calls `read_dev_supers()` for each super mirror offset.
3. Valid superblocks are added to `good_supers`; corrupted readable locations go to `bad_supers`.
4. Valid superblocks older than the maximum observed generation are moved to `bad_supers`.
5. If no bad supers exist, reports no recovery needed.
6. Otherwise asks for confirmation unless `yes` is set.
7. Opens the ctree from the first good superblock using `OPEN_CTREE_RECOVER_SUPER | OPEN_CTREE_WRITES`.
8. Resets `super_bytenr` to the primary super offset and calls `write_all_supers()`.

## State

- `struct btrfs_recover_superblock` owns the scanned device set, good/bad lists, and maximum generation.
- `struct super_block_record` stores device name, superblock copy, and bytenr.

## Dependencies

Uses device scanning, superblock reads, list helpers, super writers, and normal ctree open/close paths.

## Risks And Edge Cases

- The implementation assumes at least one good superblock remains if bad superblocks exist; it takes the first good record before rewriting.
- Recovery rewrites all superblock mirrors and can destroy non-Btrfs data if pointed at the wrong device; the command-level wrapper also checks mount status.
- Return codes are user-facing status values rather than plain negative errno.

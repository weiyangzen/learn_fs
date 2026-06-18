# File Research: sources/os/bsd/freebsd-src/sbin/fsck_msdosfs/check.c

## Purpose

Top-level filesystem check driver for `fsck_msdosfs`.

## Main Entry Point

- `checkfilesys(const char *fname)`

## Flow

1. Opens the device read-write, falling back to read-only.
2. Reads and validates the boot block with `readboot()`.
3. In preen mode with `skipclean`, checks the FAT dirty flag and skips clean filesystems.
4. Phase 1: reads FAT and builds chain ownership state with `readfat()`.
5. Phase 2: initializes directory checking, then scans the directory tree with `handleDirTree()`.
6. Phase 3: checks for lost FAT chains with `checklost()`.
7. Writes FAT changes with `writefat()` only after directory/lost-chain processing.
8. Prints file/free/bad-cluster statistics.
9. Optionally marks FAT16/FAT32 filesystems clean via `cleardirty()`.
10. Releases directory state, FAT descriptor, and file descriptor.

## Integration Points

Coordinates `boot.c`, `fat.c`, `dir.c`, and shared prompting/diagnostic functions.

## Risk Notes

`mod` is a bitmask combining fatal, repair, dirty, and unresolved-error state. The deferred FAT write is intentional: directory repairs can depend on in-memory FAT state before final persistence.

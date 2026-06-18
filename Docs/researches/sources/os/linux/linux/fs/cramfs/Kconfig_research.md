# File Research: sources/os/linux/linux/fs/cramfs/Kconfig

## Purpose
Defines build options for the compressed ROM filesystem driver.

## Main Elements
- `CRAMFS`: tristate read-only compressed filesystem support, selecting `ZLIB_INFLATE`.
- `CRAMFS_BLOCKDEV`: optional block-device image support, default enabled when block support exists.
- `CRAMFS_MTD`: optional direct physical-memory/MTD mapped image support, default enabled when blockdev mode is unavailable.

## Dependencies And Integration
Controls whether `inode.o` can mount cramfs images via normal block devices, MTD direct mapping, or both.

## Risk Notes
The help text emphasizes cramfs format limits: read-only, 256MB filesystem, 16MB files, limited uid/gid support, no hard links, and no timestamps.

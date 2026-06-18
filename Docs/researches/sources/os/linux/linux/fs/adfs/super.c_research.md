# File Research: sources/os/linux/linux/fs/adfs/super.c

Implements ADFS mount, superblock, options, probing, statfs, inode cache, and module registration.

Key behavior:
- Provides ADFS logging helpers.
- Validates ADFS disk records:
  - Sector size must be 256/512/1024 bytes.
  - `idlen` must fit format limits.
  - Filesystem must fit 32-bit sector offsets.
  - Reserved fields must be zero.
- Mount options:
  - `uid`
  - `gid`
  - `ownmask`
  - `othmask`
  - `ftsuffix`
- Reconfigure syncs the filesystem and copies parsed option state.
- `adfs_statfs()` uses map-derived block/free counts and sets magic, max name length, block size, and fsid.
- Creates/destroys a slab cache for ADFS inodes.
- `adfs_drop_inode()` always drops inodes for read-only mounts or builds without write support.
- `adfs_probe()` reads candidate disk-record locations, adjusts block size to the filesystem sector size, and reads the map.
- Supports validation through the boot block disk record or a disk record at block zero.
- `adfs_fill_super()`:
  - Sets superblock flags/magic/time granularity.
  - Probes filesystem metadata.
  - Chooses F or F+ directory ops based on disk format version.
  - Adjusts name length for optional filetype suffix.
  - Installs dentry operations.
  - Synthesizes the root object and creates the root dentry.
- Registers the block-backed `adfs` filesystem requiring a device.

Important interactions:
- `super.c` selects the directory format implementation used by `dir.c`.
- Mount fails if disk record or map validation fails.

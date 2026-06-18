# File Research: sources/local-fs/xfsprogs/mkfs/xfs_mkfs.c

## Purpose
Main implementation of `mkfs.xfs`. It parses CLI and config-file options, validates feature and geometry combinations, initializes devices and on-disk metadata, populates the root filesystem, and marks the new XFS filesystem complete.

## Key Elements
The file uses table-driven option definitions for block, config, data, inode, log, naming, proto, realtime, sector, and metadata options. Each option table records suboption names, INI section names, conflicts, range checks, unit conversion behavior, power-of-two requirements, and defaults.

Parsing flows through `parse_subopts`, option-family parser functions, and optional INI parsing via `ini_parse`. `cli_params` stores user input and delayed string conversions; `mkfs_params` stores validated/calculated filesystem geometry; `mkfs_default_params` stores build-time defaults.

Validation covers device type and overwrite checks, block/sector/log sector sizes, zoned topology, feature dependencies, directory and inode sizes, realtime extent size, data/log/realtime device sizes, stripe factors, allocation group geometry, realtime group or zone geometry, max inode percentage, atomic-write limits, log sizing/alignment, extent-size hints, and support policy.

Feature policy enforces CRC-v5 requirements for modern features, emits deprecation warnings for V4 and ascii-ci formats, auto-enables or disables features for autofsck, realtime, metadir, parent pointers, exchange-range, persistent quota flags, reflink, zoned mode, and atomic writes.

The creation path discards or resets devices when requested, initializes libxfs buffer targets, clears stale filesystem signatures and old XFS secondary superblocks, writes the bootstrap superblock and cleared log, mounts through libxfs, initializes AG headers and AGFL free space, creates realtime superblock if needed, calls `setup_proto`/`parse_proto`, checks root inode placement, verifies realtime metadata preallocation, rewrites selected secondary superblocks with root/metadir inode numbers, sets autofsck fs property, clears `sb_inprogress`, unmounts, and destroys libxfs state.

## Dependencies
Depends on libxfs, libxcmd, libfrog geometry/conversion/properties/zones/hash self-tests, Linux block/zoned ioctls, INI parser support, and `mkfs/proto.h`.

## Behavior/Risks
The file is the policy center for mkfs; small changes can affect on-disk format defaults, kernel compatibility, repair assumptions, and performance geometry. `check_root_ino` intentionally fails formatting if root inode placement diverges from xfs_repair expectations. Dry-run mode prints geometry before writing. CRC32C and dir/attr hash self-tests gate actual filesystem creation.

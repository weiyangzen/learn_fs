# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_rtalloc.h

## Purpose
Declares realtime allocation, realtime mount, realtime growfs, and realtime geometry helpers.

## Main API
With `CONFIG_XFS_RT`, the header declares realtime superblock read/free, mount initialization, rt metadata inode loading/unloading, realtime growfs, free-extent counter rebuild, geometry checking, and rtgroup allocation.

`xfs_rtallocate_rtgs` remains declared outside the feature guard because allocation call sites can reference it directly when realtime support is built into the surrounding configuration.

## Configuration Behavior
Without `CONFIG_XFS_RT`, growfs returns `-ENOSYS`, free-counter rebuild and rtsb read are no-ops, mount initialization permits filesystems without realtime blocks and rejects realtime volumes with a warning, and geometry checking succeeds trivially.

## Dependencies
The header is the public boundary between realtime allocation internals, mount code, growfs ioctl handling, and bmap allocation paths.

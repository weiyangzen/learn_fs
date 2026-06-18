# File Research: sources/os/linux/linux-stable/fs/gfs2/Kconfig

## Purpose
Defines kernel configuration entries for GFS2 and optional DLM-based cluster locking.

## Key Interfaces
- `CONFIG_GFS2_FS` builds GFS2 as tristate filesystem support.
- `CONFIG_GFS2_FS_LOCKING_DLM` enables multi-node DLM locking support.

## Design Notes
GFS2 selects buffer heads, POSIX ACL support, CRC32, quota control, and iomap support. The help text describes GFS2 as a cluster filesystem for shared block devices, with built-in nolock support and optional DLM for clustered deployments.

## Dependencies
DLM locking depends on GFS2, networking, configfs, sysfs, and DLM availability compatible with the GFS2 build mode.

## Risks And Invariants
Cluster use generally requires DLM; local/nolock mode is built in by default.

# File Research: sources/teaching/minix/minix/fs/isofs/proto.h

This header declares isofs function prototypes.

Coverage:
- Inode cache/reference functions.
- Directory and inode parsing.
- Readlink, mount, mountpoint, unmount, lookup.
- Read and getdents.
- Stat/statvfs.
- Volume descriptor read/release.
- SUSP and Rock Ridge parsing.
- Utility functions for inode entry/extents, extent block reads, ISO date conversion, and allocation.

Role:
- Defines module boundaries for the isofs server.
- Shows the server’s read-only fsdriver-facing API.

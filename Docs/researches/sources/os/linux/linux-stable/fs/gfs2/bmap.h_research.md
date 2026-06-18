# File Research: sources/os/linux/linux-stable/fs/gfs2/bmap.h

## Purpose
Declares GFS2 block mapping, iomap, truncate, allocation, journal extent, and hole punching interfaces.

## Key Interfaces
- `gfs2_write_calc_reserv()` estimates data and indirect block reservations for writes.
- Extern iomap tables: `gfs2_iomap_ops`, `gfs2_iomap_write_ops`, `gfs2_writeback_ops`.
- Declares mapping/allocation helpers, size-changing helpers, journal extent helpers, allocation-required checks, and `__gfs2_punch_hole()`.

## Design Notes
Reservation calculation accounts for direct data blocks plus indirect tree growth using the filesystem pointer geometry.

## Dependencies
Uses Linux iomap types and GFS2 inode/superblock internals.

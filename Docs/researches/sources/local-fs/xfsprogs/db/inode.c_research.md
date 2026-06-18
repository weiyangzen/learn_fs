# File Research: sources/local-fs/xfsprogs/db/inode.c

## Purpose
Defines xfs_db inode field layouts, inode-printing helpers, inode navigation, inode fork sizing/count predicates, and inode CRC recalculation.

## Main Interfaces
- Registers `inode` through `inode_init()`.
- Exports field tables for inode headers, CRC inode headers, core fields, v3 fields, data fork fields, attr fork fields, and timestamps.
- Exports printers `fp_dinode_fmt()` and `fp_metatype()`.
- Exports sizing/type helpers `inode_size()`, `inode_u_size()`, `inode_a_size()`, `inode_next_type()`, `set_cur_inode()`, and `xfs_inode_set_crc()`.

## Control Flow
The field tables describe core dinode fields, version-dependent fields, feature bits, fork unions, and metadata-inode fields. Count and offset callbacks hide or reveal fields based on inode version, CRC/v3 state, metadata flag, large extent count flag, fork format, mode, and attr fork offset. `inode_f()` either reports the current inode or calls `set_cur_inode()`. `set_cur_inode()` validates AG/inode math, chooses inode-cluster-sized IO where needed to match libxfs buffer caching, reads the containing inode buffer, offsets the cursor to the selected inode, records inode/mode/dirino state, verifies inode CRC when supported, and adds the location to the ring.

## Dependencies
Relies on libxfs dinode layout macros, inode geometry, bmap extent-count helpers, type and field subsystems, IO cursor stack, bit printers, and global mount state.

## Risks And Invariants
- Inode reads deliberately use cluster buffers to avoid overlapping-buffer cache problems with libxfs.
- Many field callbacks assert they are operating on `iocur_top->data`; they are tightly coupled to current cursor state.
- Large extent count support switches `nextents`/`anextents` field widths and offsets.
- `inode_next_type()` maps regular metadata inodes to quota, realtime bitmap/summary, rtrmap, rtrefcount, or plain data based on filesystem feature state and inode identity.

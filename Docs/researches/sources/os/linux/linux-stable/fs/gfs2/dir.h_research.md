# File Research: sources/os/linux/linux-stable/fs/gfs2/dir.h

## Purpose
Declares GFS2 directory APIs, directory-add state, qstr helpers, and on-disk dirent initialization helpers.

## Key Interfaces
- `struct gfs2_diradd` carries allocation/addition state including block count, target dirent, buffer, and save flag.
- Declares directory search/check/add/delete/read/move, exhash deallocation, allocation-required probing, new directory buffer allocation, and hash invalidation.
- Defines `gfs2_disk_hash()`, `gfs2_str2qstr()`, and `gfs2_qstr2dirent()`.

## Dependencies
Uses Linux dcache/qstr, CRC32, GFS2 inode and dirent structures, and buffer heads.

## Risks And Invariants
`gfs2_qstr2dirent()` initializes empty inode fields and copies exactly `name->len` bytes with no terminator, matching on-disk dirent layout.

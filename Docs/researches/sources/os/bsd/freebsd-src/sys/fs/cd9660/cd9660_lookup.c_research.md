# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_lookup.c

## Purpose
Implements directory component lookup and directory-block reading for cd9660.

## Main Elements
- `cd9660_lookup()` searches ISO directory records for the requested component, including `.` and `..`.
- Supports associated files via leading `=` for non-RRIP filesystems.
- Uses cached `i_diroff` for repeated lookups and may perform a two-pass search.
- Handles default ISO/Joliet name comparison through `isofncmp()`.
- Handles Rock Ridge names and relocated directory links through `cd9660_rrip_getname()`.
- Returns `EROFS` for create/rename attempts on missing entries.
- Copies directory records before vnode lookup when needed to avoid vnode/buffer lock-order reversal.
- Uses `vn_vget_ino_gen()` for `..` deadlock avoidance.
- Inserts positive and negative namecache entries when requested.
- `cd9660_blkatoff()` reads the directory block for an offset and ensures `b_blkno` is mapped for inode-number calculations.

## Dependencies And Integration
Uses ISO directory format helpers, Rock Ridge helpers, vnode cache, buffer cache, and cd9660 vnode retrieval.

## Risk Notes
Lookup relies on strict directory record validation to avoid malformed media crossing block boundaries or using illegal record lengths.

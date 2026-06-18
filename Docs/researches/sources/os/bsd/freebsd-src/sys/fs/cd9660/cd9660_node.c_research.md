# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_node.c

## Purpose
Implements cd9660 inode lifecycle helpers and default ISO attribute/timestamp conversion.

## Main Elements
- `cd9660_inactive()` recycles vnodes whose ISO mode is cleared.
- `cd9660_reclaim()` removes the vnode from the VFS hash and frees the `iso_node`.
- `cd9660_defattr()` derives file type, mode, link count, uid, and gid from ISO directory records or extended attributes.
- `cd9660_deftstamp()` derives atime/mtime/ctime from extended attributes or directory-record timestamps.
- `cd9660_tstamp_conv7()` converts 7-byte ISO timestamps with timezone adjustment and pre-1970 clamping.
- `cd9660_tstamp_conv17()` converts 17-byte timestamps by feeding normalized fields into the 7-byte converter.
- `isodirino()` computes an inode number from extent plus extended attribute length.

## Dependencies And Integration
Used by VFS vnode construction, lookup, and Rock Ridge fallback/default logic.

## Risk Notes
Timestamp conversion tolerates unreliable timezone fields by accepting only a bounded offset range.

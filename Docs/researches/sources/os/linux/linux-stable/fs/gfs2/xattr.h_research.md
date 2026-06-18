# File Research: sources/os/linux/linux-stable/fs/gfs2/xattr.h

## Scope

This header defines GFS2 extended attribute layout macros, request/location helper structures, and exported xattr functions.

## APIs And Definitions

- Length and layout macros: `GFS2_EA_REC_LEN()`, `GFS2_EA_DATA_LEN()`, `GFS2_EA_SIZE()`, `GFS2_EA_IS_STUFFED()`, `GFS2_EA_IS_LAST()`, `GFS2_EAREQ_SIZE_STUFFED()`.
- Pointer macros map an EA header to name bytes, stuffed data bytes, unstuffed data pointer array, next record, and first EA record in a buffer.
- `struct gfs2_ea_request` carries type, name, value pointer, and lengths for set/write paths.
- `struct gfs2_ea_location` returns the containing buffer, matching EA record, and previous EA record.
- Exports: `__gfs2_xattr_set()`, `gfs2_listxattr()`, `gfs2_ea_dealloc()`, and ACL helper `gfs2_xattr_acl_get()`.

## Invariants

The layout macros assume validated on-disk EA headers and big-endian length fields. Callers must hold the appropriate inode glock for reading or writing EA blocks. Unstuffed pointer arrays start after the name rounded to an 8-byte boundary.

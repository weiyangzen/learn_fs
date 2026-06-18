# File Research: sources/os/linux/linux-stable/fs/gfs2/acl.h

## Purpose
Declares GFS2 ACL interfaces and the maximum ACL entry calculation.

## Key Interfaces
- `GFS2_ACL_MAX_ENTRIES(sdp)` computes a block-size-scaled ACL entry cap.
- Declares `gfs2_get_acl()`, `__gfs2_set_acl()`, and `gfs2_set_acl()`.

## Dependencies
Includes `incore.h` for GFS2 internal structures and relies on Linux POSIX ACL types through included headers.

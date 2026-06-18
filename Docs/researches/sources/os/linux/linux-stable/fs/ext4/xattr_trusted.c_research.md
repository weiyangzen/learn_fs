# File Research: sources/os/linux/linux-stable/fs/ext4/xattr_trusted.c

## Purpose
Provides ext4 handling for `trusted.*` extended attributes.

## Main Components
- Listing is restricted to callers with `CAP_SYS_ADMIN`.
- Get/set delegate to core ext4 xattr functions with `EXT4_XATTR_INDEX_TRUSTED`.

## Exported Interface
Defines `ext4_xattr_trusted_handler` with `XATTR_TRUSTED_PREFIX`.

## Research Notes
Capability-based visibility is handled at the namespace adapter layer; storage is shared with the rest of ext4 xattrs.

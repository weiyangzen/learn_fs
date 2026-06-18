# File Research: sources/os/bsd/freebsd-src/sys/fs/cd9660/cd9660_mount.h

## Purpose
Defines user-visible mount arguments and mount flags for ISO 9660/cd9660 filesystems.

## Main Elements
- `struct iso_args` includes device path, export args, uid/gid, file and directory masks, flags, starting sector, and optional disk/local charset names.
- Flags include disabling Rock Ridge, generation numbers, extended attributes, disabling/allowing broken Joliet, kernel iconv conversion, and uid/gid overrides.

## Dependencies And Integration
Used by mount code and userland mount_cd9660 ABI.

## Risk Notes
This header is part of the mount ABI; field or flag changes affect userland compatibility.

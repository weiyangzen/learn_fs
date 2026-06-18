# File Research: sources/os/bsd/netbsd-src/sys/fs/cd9660/cd9660_mount.h

## Summary
Defines public mount arguments and mount flag bits for ISO 9660 filesystems.

## Main Responsibilities
- Define `struct iso_args` with device path, flags, uid, gid, file mask, and directory mask.
- Define flags to disable Rock Ridge, enable generation numbers, enable extended attributes, disable Joliet, disable case translation, enable case-insensitive Rock Ridge, and override uid/gid.
- Define printable bit description `ISOFSMNT_BITS`.

## Integration Notes
Userland mount tools and kernel mount code share this structure and flag layout.

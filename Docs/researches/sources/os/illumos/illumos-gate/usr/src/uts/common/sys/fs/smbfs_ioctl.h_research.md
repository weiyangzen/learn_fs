# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fs/smbfs_ioctl.h

This header defines project-private SMBFS ioctl payloads and command numbers.

Payload:
- `ioc_sdbuf_t` describes a user-space security descriptor buffer with address, allocated size, used size, and selector such as DACL security information.

Ioctls:
- `SMBFSIO_GETSD` uses `_IO('f', 81)`.
- `SMBFSIO_SETSD` uses `_IO('f', 82)`.
- Both use `ioc_sdbuf_t` data.

Dependencies and relationships:
- Provides SMBFS-specific get/set security descriptor operations.
- Reuses FS-specific ioctl number space from `sys/filio.h`.

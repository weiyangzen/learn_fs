# File Research: sources/local-fs/erofs-utils/lib/backends/nbd.c

## Purpose
Implements Linux Network Block Device helper functions for serving or managing EROFS images through `/dev/nbd*`, using ioctl and optionally generic netlink.

## Main Areas
- NBD ioctl constants and protocol request/reply magic.
- Device state probing through `/sys/block/nbdX`.
- Legacy ioctl connection setup using `socketpair()`.
- Optional libnl generic-netlink connect/reconnect/reconfigure/disconnect.
- NBD request parsing and reply header writing.

## Important Functions
- `erofs_nbd_in_service()`: checks `/sys/block/nbdN/size` and `pid` to determine if a device is connected and returns pid or negative errno.
- `erofs_nbd_devscan()`: scans `/sys/block` for an apparently unused `nbdX`.
- `erofs_nbd_connect()`: creates a socketpair, configures block size, block count, timeout, read-only flags, and socket through ioctls.
- `erofs_nbd_get_identifier()`: reads `/sys/block/nbdN/backend`.
- `erofs_nbd_get_index_from_minor()`: maps NBD minor to `nbdX` by reading `/sys/dev/block/<major>:<minor>/uevent`.
- `erofs_nbd_nl_connect()`, `erofs_nbd_nl_reconnect()`, `erofs_nbd_nl_reconfigure()`, `erofs_nbd_nl_disconnect()`: generic-netlink NBD operations when available; stubs return `-EOPNOTSUPP` otherwise.
- `erofs_nbd_do_it()`: runs `NBD_DO_IT` and treats expected `EPIPE` disconnect as success.
- `erofs_nbd_get_request()`: reads and byte-swaps an NBD request.
- `erofs_nbd_send_reply_header()`: writes the protocol reply header.
- `erofs_nbd_disconnect()`: issues disconnect and clears socket.

## Interactions
- Uses `erofs_io_read`, `erofs_vfile`, `erofs_strerror`, and logging helpers.
- Linux-only source selected by `OS_LINUX` in `lib/Makefile.am`.

## Notes
The code supports both older ioctl setup and newer netlink setup; netlink support is compile-time optional.

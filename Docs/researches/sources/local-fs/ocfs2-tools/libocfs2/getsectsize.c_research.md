# File Research: sources/local-fs/ocfs2-tools/libocfs2/getsectsize.c

Purpose: determines the hardware sector size of a device.

Key API:
- `ocfs2_get_device_sectsize()`

Behavior:
- Opens the path read-only with `open64()` when available.
- Maps `ENOENT` to `OCFS2_ET_NAMED_DEVICE_NOT_FOUND`; other open failures return `OCFS2_ET_IO`.
- Uses Linux `BLKSSZGET` ioctl when available.
- Returns `OCFS2_ET_CANNOT_DETERMINE_SECTOR_SIZE` if the ioctl path is unavailable or fails.
- Closes the file descriptor before returning.

Dependencies:
- Linux block ioctl definitions when available.
- `ocfs2/ocfs2.h` error codes.

Notable behavior:
- There is no regular-file fallback; this helper is device-sector focused.
- `heartbeat.c` treats `OCFS2_ET_CANNOT_DETERMINE_SECTOR_SIZE` as recoverable and falls back to `OCFS2_MIN_BLOCKSIZE`.

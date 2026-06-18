# File Research: sources/local-fs/gfs2-utils/gfs2/libgfs2/device_geometry.c

This file gathers device/file geometry for GFS2 tools.

Public APIs:
- `lgfs2_get_dev_info(fd, info)`: fills `lgfs2_dev_info` from `fstat()`, block ioctls, access mode, and file/device size.
- `lgfs2_fix_device_geometry(sdp)`: converts byte size to filesystem-block count in `sdp->device.length`.

Behavior:
- Accepts regular files and block devices.
- Rejects other file types with `ENOTBLK`.
- For regular files, uses `st_size`, `F_GETFL`, and `st_blksize`.
- For block devices, probes read-ahead, logical/physical block sizes, IO alignment, readonly state, and size via `lseek(SEEK_END)`.
- Rejects devices smaller than 1 MiB with `ENOSPC`.

Risk notes:
- Several ioctls are best-effort and unchecked; unavailable values remain zero.
- `lseek(SEEK_END)` determines block-device size, so unusual devices may fail.
- `lgfs2_fix_device_geometry()` assumes `sdp->sd_bsize` is initialized.

# File Research: sources/virtualization/spdk/lib/util/fd.c

This file provides small file-descriptor utilities for device geometry, file size, and nonblocking mode.

`spdk_fd_get_blocklen()` queries sector/block length with platform-specific ioctls: FreeBSD `DIOCGSECTORSIZE`, `DKIOCGETBLOCKSIZE` where available, or Linux `BLKSSZGET`. It returns zero when no supported query succeeds.

`spdk_fd_get_size()` uses `fstat()` to reject symlinks, return regular-file size, and query block/character device size via `dev_get_size()`. Device size uses FreeBSD `DIOCGMEDIASIZE` or Linux `BLKGETSIZE64`; unsupported or failed cases return zero.

`spdk_fd_set_nonblock()` and `spdk_fd_clear_nonblock()` share `fd_update_nonblock()`, which reads `F_GETFL`, updates `O_NONBLOCK` only when needed, and writes `F_SETFL`. Errors are logged with `spdk_strerror()` and returned as negative errno.

The main dependency is POSIX file status and fcntl/ioctl behavior. Callers must treat zero size/block length as “unknown or unsupported,” not necessarily a valid zero-length device.

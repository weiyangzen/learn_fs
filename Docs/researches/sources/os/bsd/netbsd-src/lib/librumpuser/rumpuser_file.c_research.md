# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_file.c

## Summary
POSIX file and device helper hypercalls for rumpuser.

## Key Details
- `rumpuser_getfileinfo` classifies paths as directory, regular file, block device, character device, or other.
- For device sizes, it tries NetBSD disklabel and wedge ioctls when available; otherwise it falls back to `lseek(fd, 0, SEEK_END)` and reports unsupported if that fails.
- `rumpuser_open` maps rump open flags to host `open` flags and wraps the blocking call with kernel unschedule/reschedule.
- `rumpuser_close` unschedules, calls `fsync`, closes the fd, and reschedules.
- Vector reads/writes cast `struct rumpuser_iovec` to `struct iovec`, using `readv`/`writev`, `preadv`/`pwritev` when available, or lseek-plus-vector-I/O fallback under unscheduling.
- `rumpuser_syncfd` validates sync flags and uses `fsync_range` when available, otherwise `fsync`.

## Notes
The file notes this code is expected to move to a new driver in a future hypercall revision.

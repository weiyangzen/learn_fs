# File Research: sources/local-fs/ntfs-3g/libntfs-3g/unix_io.c

Implements the Unix/POSIX `ntfs_device_operations` backend for libntfs-3g. It stores a heap-allocated file descriptor in `dev->d_private`, opens regular files or block devices, tags block devices with `NDevSetBlock`, tracks read-only and dirty state through `NDev*` flags, and exposes seek/read/write/pread/pwrite/sync/stat/ioctl operations.

Open logic validates the path with `stat()`, uses `O_EXCL` for read-write regular-file mounts, retries permission-denied read-write opens as `EROFS`, checks Linux block-device read-only state with `BLKROGET`, and applies advisory whole-file read or write locks through `fcntl(F_SETLK)`. Close fsyncs dirty devices, unlocks, closes, clears open state, and frees private storage.

The sync path uses `ntfs_fsync()`, which maps to macOS `F_FULLFSYNC` with `fsync()` fallback on Darwin and plain `fsync()` elsewhere. Writes and positioned writes refuse read-only devices with `EROFS`, mark the device dirty before calling `write()`/`pwrite()`, and otherwise delegate directly to POSIX syscalls.

Dependencies are `ntfs_device`, `device.h` flag macros, POSIX file APIs, optional Linux block ioctls, and NTFS logging helpers. Important invariants are that `d_private` is a valid `int *` only while `NDevOpen` is set, dirty state is cleared only by successful sync, and lock failures prevent mounting rather than allowing concurrent writes.

# File Research: sources/local-fs/apfs-fuse/ApfsLib/DeviceLinux.cpp

This Linux-only implementation opens a path read-only with `O_LARGEFILE`, determines size via `fstat64` for regular files or `BLKGETSIZE64` for block devices, and reads via `pread64`.

`Close()` closes the file descriptor and resets size. Destructor calls `Close()`.

The class logs open failures and optional debug info using `g_debug`.

Notable risk: `Read()` stores `pread64()` result in `size_t`; errors return `-1`, which converts to a large unsigned value. The equality check still fails for ordinary lengths, but the type is semantically wrong.

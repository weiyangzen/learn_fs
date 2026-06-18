# File Research: sources/os/bsd/netbsd-src/sys/fs/filecorefs/filecore_utils.c

Read completely: 356 lines.

Provides FileCore utility functions. `filecore_bbchecksum()` validates the 512-byte boot block checksum while rejecting degenerate blocks containing all identical bytes, because such blocks would otherwise checksum trivially.

`filecore_mode()` maps FileCore read/owner-read/directory attributes plus mount policy flags into NetBSD mode bits, including directory execute bits and regular-vs-directory file type. `filecore_time()` converts FileCore load/exec timestamp fields into a `timespec` using the RISC OS centisecond epoch adjustment.

`filecore_getparent()` resolves and caches a directory’s parent by reading the directory tail and, when needed, scanning the grandparent directory for the entry pointing back to the current directory. Root’s parent is itself. `filecore_fn2unix()` converts FileCore names to Unix names by replacing `/` with `.`, and `filecore_fncmp()` performs case-insensitive comparison with Unix `.` mapped back to FileCore `/`.

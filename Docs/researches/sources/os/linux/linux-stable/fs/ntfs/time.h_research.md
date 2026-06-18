# File Research: sources/os/linux/linux-stable/fs/ntfs/time.h

This header implements inline conversion between Linux `timespec64` UTC timestamps and NTFS little-endian timestamp values.

Main responsibilities:
- Defines `NTFS_TIME_OFFSET`, the seconds between the NTFS epoch, January 1, 1601 UTC, and the Unix epoch, January 1, 1970 UTC.
- Converts Linux time to NTFS 100 ns units with `utc2ntfs()`.
- Gets current coarse realtime and converts it with `get_current_ntfs_time()`.
- Converts little-endian NTFS timestamps back to `struct timespec64` with `ntfs2utc()`.

Important functions:
- `utc2ntfs()` adds the epoch offset, multiplies seconds by 10,000,000, adds `tv_nsec / 100`, and returns `cpu_to_le64()`.
- `ntfs2utc()` subtracts the offset in 100 ns units, uses `div_s64_rem()` to split seconds and remainder, and converts the remainder to nanoseconds.

Research notes:
- The file is header-only for cheap use in inode and metadata timestamp paths.
- All on-disk NTFS values are represented as little-endian `__le64`.

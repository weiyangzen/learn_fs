# File Research: sources/os/linux/linux/fs/ntfs/time.h

Read coverage: complete file, 87 lines.

This header provides inline conversion helpers between Linux `timespec64` UTC timestamps and NTFS timestamps.

Key definitions:
- `NTFS_TIME_OFFSET` is the seconds offset between 1601-01-01 UTC and 1970-01-01 UTC.
- `utc2ntfs()` converts seconds/nanoseconds to 100 ns NTFS ticks and returns little-endian `__le64`.
- `get_current_ntfs_time()` uses `ktime_get_coarse_real_ts64()` then `utc2ntfs()`.
- `ntfs2utc()` converts little-endian NTFS ticks back to `struct timespec64` using `div_s64_rem()`.

Integration:
- Used anywhere the NTFS driver must read/write on-disk NTFS time fields.
- Handles endian conversion at the conversion boundary.

Risks:
- Negative NTFS-to-Unix conversions rely on signed division/remainder behavior. Callers should expect `tv_nsec` derived from a signed remainder for pre-1970 times.

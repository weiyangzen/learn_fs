# File Research: sources/local-fs/ntfs-3g/libntfs-3g/win32_io.c

Implements the Windows `ntfs_device_operations` backend for libntfs-3g. It supports regular image files, whole physical drives, `/dev/hdX`-style partitions, and drive-letter volumes, with separate paths for Win32 APIs and lower-level NT native APIs.

The backend defines a `win32_fd` state object containing handles, logical position, partition offset/length, hidden-sector count, geometry, NTFS volume size, optional volume handle, and whether NT native calls are used. It dynamically imports `FindFirstVolume`, `FindNextVolume`, `FindVolumeClose`, and `SetFilePointerEx`, with a `SetFilePointer`-based fallback for older Windows.

Open helpers translate Unix access flags to Win32 access masks, open regular files with `CreateFile`, mark writable files sparse when possible, open physical drives, query drive geometry and length, locate partition extents from drive-layout ioctls, find matching mounted volume handles by enumerating `IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS`, and lock writable volumes. Drive-letter open uses `NtOpenFile`, NT read/write calls, and `FSCTL_ALLOW_EXTENDED_DASD_IO`.

I/O paths handle Windows sector alignment requirements. Aligned positioned reads/writes go through `ntfs_device_win32_pio()`. Unaligned reads allocate an aligned buffer, round the range to sector boundaries, read through the volume handle when the request lies inside NTFS-accessible space and through the physical handle otherwise, copy out the requested byte range, and update logical position. Unaligned writes read boundary sectors first, merge caller bytes, write aligned sectors, handle crossing from volume to disk extent, mark the device dirty, and reject read-only writes.

Close dismounts and unlocks writable volume handles, closes both volume and disk/file handles, clears open state, and frees the private `win32_fd`. Sync flushes the volume handle and backing handle when dirty. Stat fills a Unix-like `struct stat` with mode, size, and block count. Ioctl emulation handles block size/size/geometry requests where enabled and treats block-size set as a no-op.

The file also provides Windows helpers used by `ntfsclone`: `ntfs_win32_set_sparse()`, `ntfs_device_win32_ftruncate()`, and `ntfs_win32_ftruncate()`.

Dependencies include Windows kernel32 APIs, `winioctl.h`, NT native file APIs, libntfs device flags, geometry ioctl constants, optional Linux-compatible ioctl names, and NTFS logging/memory helpers. Important invariants are sector alignment for raw Windows volume I/O, correct distinction between logical volume offsets and physical partition offsets, dirty-state flushing before close, and exclusive locking for writable volume access.

# File Research: sources/os/linux/linux/fs/xfs/xfs_platform.h

## Purpose

`xfs_platform.h` is the Linux-kernel platform adaptation header for XFS. It pulls in kernel headers, defines XFS platform types and constants, maps XFS configuration options to compile-time flags, wires assertion/corruption helpers, and provides small portability wrappers.

## Main Responsibilities

- Include Linux kernel APIs needed broadly by XFS.
- Define core XFS scalar types such as `xfs_off_t`, `xfs_ino_t`, `xfs_daddr_t`, `xfs_dev_t`, and `xfs_nlink_t`.
- Include foundational XFS headers used widely across the subsystem.
- Map `CONFIG_XFS_*` options to `DEBUG`, `DEBUG_EXPENSIVE`, `XFS_ASSERT_FATAL`, and `XFS_WARN`.
- Expose sysctl parameter aliases such as `xfs_panic_mask`, `xfs_error_level`, and timer settings.
- Define block-device I/O constants and error aliases.
- Provide assertion macros and corruption-detection macro.
- Provide realtime inode/mount predicates based on `CONFIG_XFS_RT`.
- Provide pointer-format policy for debug vs non-debug builds.
- Provide `kmem_to_page` for vmalloc or direct kernel memory.

## Important Macros and Helpers

- `current_cpu`, `current_set_flags_nested`, `current_restore_flags_nested`
- `BLKDEV_IOSHIFT`, `BLKDEV_IOSIZE`, `BLKDEV_BB`
- `ENOATTR`, `EWRONGFS`
- `__this_address`: label-address helper protected by `barrier`.
- `howmany`
- `delay`: uninterruptible schedule timeout wrapper.
- `xfs_to_linux_dev_t` and `linux_to_xfs_dev_t`
- `xfs_sort`
- `xfs_stack_trace`
- `rounddown_64`, `roundup_64`, `howmany_64`, `isaligned_64`
- `log2_if_power2`, `mask64_if_power2`
- `ASSERT_ALWAYS`, `ASSERT`
- `XFS_IS_CORRUPT`
- `STATIC`: defined as `static noinline`
- `XFS_IS_REALTIME_INODE`, `XFS_IS_REALTIME_MOUNT`
- `PTR_FMT`
- `kmem_to_page`

## Assertion Behavior

In debug builds, `ASSERT` calls `assfail`. In non-debug builds with `XFS_WARN`, it calls `asswarn`; otherwise it compiles out. `ASSERT_ALWAYS` always calls `assfail` on failure.

## Dependencies

This header includes many XFS subsystem headers, including stats, sysctl, iops, aops, superblock, checksum, buffer, message, drain, and hooks headers. It is a foundational include for most XFS C files.

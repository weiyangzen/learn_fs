# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_platform.h

## Purpose
Provides the Linux-kernel platform layer for XFS: common kernel includes, XFS scalar typedefs, configuration-derived debug macros, global parameter aliases, platform utility wrappers, assertions, corruption detection, realtime feature helpers, and memory-to-page conversion.

## Main Contents
Defines XFS core integer types such as `xfs_off_t`, `xfs_ino_t`, `xfs_daddr_t`, `xfs_dev_t`, and `xfs_nlink_t`. It includes major XFS internal headers needed widely by implementation files and maps XFS tunables to `xfs_params`.

## Utility Helpers
Provides device number conversion helpers, `rounddown_64`, `roundup_64`, `howmany_64`, `isaligned_64`, power-of-two log/mask helpers, `delay`, `xfs_sort`, `xfs_stack_trace`, `__this_address`, `kmem_to_page`, and `xfs_rw_bdev` declaration.

## Debug and Corruption Handling
Configuration maps enable `DEBUG`, `DEBUG_EXPENSIVE`, `XFS_ASSERT_FATAL`, and `XFS_WARN`. `ASSERT` either fails, warns, or compiles out depending on config. `XFS_IS_CORRUPT` reports metadata corruption with file/line and return-address context.

## Platform Semantics
Defines Linux equivalents for XFS attribute and wrong-filesystem errors, pointer print formatting policy, realtime inode/mount predicates that compile to false without realtime support, and the `STATIC` macro used to keep many internal functions `static noinline`.

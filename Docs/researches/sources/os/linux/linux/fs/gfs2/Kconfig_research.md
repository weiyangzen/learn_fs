# File Research: sources/os/linux/linux/fs/gfs2/Kconfig

Defines Kconfig entries for GFS2 filesystem support and optional DLM cluster locking.

Key configuration:
- `GFS2_FS` is a tristate filesystem option selecting `BUFFER_HEAD`, `FS_POSIX_ACL`, `CRC32`, `QUOTACTL`, and `FS_IOMAP`.
- `GFS2_FS_LOCKING_DLM` enables DLM locking and depends on GFS2, networking, configfs, sysfs, and DLM availability.

Purpose:
- Describes GFS2 as a shared-block cluster filesystem with immediate cross-node consistency through a lock module.
- Notes `nolock` is built in by default and DLM is needed for cluster environments.

Integration:
- Drives compilation of `fs/gfs2` objects and optional `lock_dlm.o` through the Makefile.

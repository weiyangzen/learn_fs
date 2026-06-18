# File Research: sources/os/linux/linux/fs/hfsplus/Kconfig

Purpose: Declares kernel configuration options for HFS+ filesystem support and HFS+ KUnit tests.

Key options:
- `HFSPLUS_FS` is a tristate depending on block devices, selecting buffer heads, NLS, UTF-8 NLS, and legacy direct I/O.
- `HFSPLUS_KUNIT_TEST` builds HFS+ KUnit tests when HFS+ and KUnit are enabled, defaulting under `KUNIT_ALL_TESTS`.

Dependencies and integration:
- Controls compilation of the HFS+ object list in `Makefile`.

Risk notes:
- HFS+ support is described as read-write and includes Mac metadata plus Unix-style ownership/permissions.

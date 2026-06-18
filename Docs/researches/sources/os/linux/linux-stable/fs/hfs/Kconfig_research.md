# File Research: sources/os/linux/linux-stable/fs/hfs/Kconfig

## Scope

This Kconfig file declares the Linux HFS filesystem driver and its optional KUnit tests.

## Options

- `HFS_FS` is a tristate "Apple Macintosh file system support" option. It depends on `BLOCK` and selects `BUFFER_HEAD`, `NLS`, and `LEGACY_DIRECT_IO`. As a module, it builds as `hfs`.
- Help text states that enabling it permits mounting Macintosh-formatted floppy disks and hard drive partitions with full read-write access and points to `Documentation/filesystems/hfs.rst` for mount options.
- `HFS_KUNIT_TEST` is a tristate KUnit test option, depends on `HFS_FS && KUNIT`, defaults to `KUNIT_ALL_TESTS`, and is intended for kernel developer test harnesses rather than production builds.

## Invariants

The filesystem driver assumes block-device support and old buffer-head/direct-I/O infrastructure. KUnit tests are only selectable when both HFS and KUnit are available.

# File Research: sources/local-fs/dosfstools/src/Makefile.am

Automake build definition for dosfstools command-line programs in `src`.

Key points:
- Builds installed programs: `fsck.fat`, `mkfs.fat`, and `fatlabel`.
- Builds non-installed helper: `testdevinfo`.
- Defines shared source groups:
  - `charconv_common_sources`: character conversion helpers.
  - `fscklabel_common_sources`: boot/FAT/I/O/common code shared by `fsck.fat` and `fatlabel`.
  - `devinfo_common_sources`: device probing and block-device helpers used by `mkfs.fat` and `testdevinfo`.
- Links `LIBICONV` into `fsck.fat`, `mkfs.fat`, and `fatlabel`.
- Adds `-I$(srcdir)/blkdev` for `mkfs.fat` and `testdevinfo`.
- Optional `COMPAT_SYMLINKS` install hook creates legacy command names such as `dosfsck`, `mkdosfs`, `fsck.vfat`, and `mkfs.msdos`; uninstall hook removes them.

Dependencies surfaced:
- `fsck.fat` combines checker, file-operation rules, LFN handling, boot parsing, FAT handling, and virtual I/O.
- `fatlabel` reuses the fsck/label core without directory repair.
- `mkfs.fat` uses `device_info` and `blkdev` but not the fsck directory checker.

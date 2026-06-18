# File Research: sources/local-fs/f2fs-tools/mkfs/Makefile.am

Automake build definition for mkfs formatting components.

Key contents:
- Sets include flags for libuuid/libblkid and the top-level `include` directory.
- Builds `sbin_PROGRAMS = mkfs.f2fs` from `f2fs_format_main.c`, `f2fs_format.c`, and `f2fs_format_utils.c`.
- Links `mkfs.f2fs` with libuuid, libblkid, and `libf2fs.la`.
- Installs `f2fs_fs.h` as an include header and keeps `f2fs_format_utils.h` as a non-installed header.
- Builds shared library `libf2fs_format.la` from the same formatter sources, with version-info variables.
- `install-exec-hook` moves `libf2fs_format.so.*` to `root_libdir` when configured and leaves a relative symlink in `libdir`.
- `uninstall-hook` removes root-libdir copies.

Build implications:
- `-DWITH_BLKDISCARD` and `_FILE_OFFSET_BITS=64` are applied to mkfs and formatter library builds.
- The formatter implementation is available both as a command and as a library surface.

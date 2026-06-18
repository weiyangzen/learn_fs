# File Research: sources/os/bsd/freebsd-src/sys/fs/msdosfs/msdosfs_iconv.c

Small module glue file declaring msdosfs kernel iconv support.

Main responsibilities:
- Includes kernel, module, mount, and iconv headers.
- Uses `VFS_DECLARE_ICONV(msdosfs)` to declare iconv integration state/functions for the msdosfs filesystem.

Important dependencies:
- The `msdosfs_conv.c` conversion code references `extern struct iconv_functions *msdosfs_iconv`.
- Active only when kernel iconv infrastructure is available and mounts request charset conversion.

Notable risks and edge cases:
- Contains no conversion logic itself; it is registration/declaration glue for the conversion paths.

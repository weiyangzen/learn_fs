# File Research: sources/os/linux/linux/io_uring/xattr.c

io_uring extended attribute operation implementation for getxattr/setxattr and file-based variants.

Key responsibilities:
- Prepares `getxattr`, `fgetxattr`, `setxattr`, and `fsetxattr` requests.
- Imports xattr names and, for set operations, copies value data through VFS helpers.
- Captures delayed pathnames for path-based operations.
- Forces async execution for blocking xattr operations.
- Executes file-based or pathname-based xattr VFS helpers.
- Cleans allocated xattr name/value memory and delayed filenames.

Important data flows:
- Get prep allocates `kname`, imports the xattr name, stores userspace output buffer and size, rejects get flags, and optionally captures path from `addr3`.
- Set prep allocates `kname`, calls `setxattr_copy()` to import name/value/flags, and optionally captures path from `addr3`.
- Finish clears cleanup flag, releases copied resources, and sets the CQE result.
- Path-based issue uses `filename_getxattr()` or `filename_setxattr()` with `AT_FDCWD` and `LOOKUP_FOLLOW`.

Important invariants:
- Path-based xattr operations reject fixed-file mode.
- Cleanup must free both `ctx.kname` and `ctx.kvalue` when present.
- Issue paths expect blocking context and warn on nonblocking issue.

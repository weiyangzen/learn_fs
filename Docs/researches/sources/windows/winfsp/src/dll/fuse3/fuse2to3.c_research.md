# File Research: sources/windows/winfsp/src/dll/fuse3/fuse2to3.c

This file adapts FUSE3 APIs to the existing FUSE2-based WinFsp implementation.

Key responsibilities:
- Converts `fuse_file_info` between FUSE2 and FUSE3 shapes.
- Converts FUSE2 connection info to FUSE3 connection/config structures, advertising a FUSE 3.2-era protocol view.
- Defines wrappers for most FUSE3 operations, forwarding through the active `struct fuse3` callback table:
  - metadata, namespace, file I/O, directory I/O, xattr, lifecycle, access, locking, ioctl, poll, buf I/O, flock, fallocate.
- Converts FUSE3 `readdir` filler semantics into the FUSE2 directory filler helpers in `fuse_intf.c`, including readdir-plus flags.
- Calls FUSE3 `init` with a `fuse3_config`, then maps wanted capabilities back into the FUSE2 `conn->want`.
- Copies and preflights arguments with core FUSE option parsing.
- Implements `fsp_fuse3_new`, `fsp_fuse3_new_30`, `fsp_fuse3_destroy`, `fsp_fuse3_mount`, and `fsp_fuse3_unmount`.
- Mounting builds a FUSE2 operation table of wrapper functions, creates a FUSE2 `struct fuse`, frees the temporary channel/args, and links `fuse` and `fuse3` objects together.

Filesystem relevance:
- FUSE3 support is not a separate backend; it is a compatibility layer over the FUSE2 WinFsp path.
- Any FUSE3 filesystem ultimately reaches `fuse_loop.c` and `fuse_intf.c` after callback adaptation.

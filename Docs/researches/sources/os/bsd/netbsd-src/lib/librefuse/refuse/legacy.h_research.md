# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/legacy.h

This compatibility header defines removed FUSE types and functions: old `struct fuse_statfs`, Linux-specific `struct statfs` used by FUSE 2.1-2.4, `fuse_dirh_t`, `FUSE_DEBUG`, `fuse_invalidate`, and `fuse_is_lib_option`.

Integration points: included by version headers and `fs.c` for old callback struct definitions and statfs translation. Risks are Linux/NetBSD type-layout assumptions and preserving old public API while not conflicting with native system headers.

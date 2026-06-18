# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/fs.h

This internal header declares the opaque `struct fuse_fs` and all filesystem stacking dispatchers implemented by `fs.c`. It documents the default missing-operation behavior: most return `-ENOSYS`, while open/release/opendir/releasedir/statfs return success.

Integration points: consumed by `refuse.c` and compatibility wrappers to call operation tables without caring about the exact `struct fuse_operations` version. Risk is declaration/implementation drift across many versioned function names and callback signatures.

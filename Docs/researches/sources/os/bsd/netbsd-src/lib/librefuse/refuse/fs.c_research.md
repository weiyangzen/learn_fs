# File Research: sources/os/bsd/netbsd-src/lib/librefuse/refuse/fs.c

This is the filesystem stacking compatibility layer. It wraps a versioned `struct fuse_operations_v*` table in `struct fuse_fs`, clones the operation table, stores its version and user data, and exposes version-neutral `fuse_fs_*` dispatchers.

Each dispatcher sets `fuse_get_context()->private_data` to the filesystem layer's user data, then switches on operation-table version. It adapts changed prototypes across FUSE 1.1, 2.1, 2.2, 2.3, 2.5, 2.6, 2.8, 2.9, 3.0, 3.4, 3.5, and 3.8 for getattr, rename, open/release, read/write, statfs, readdir/getdir, chmod/chown/truncate/utimens, xattrs, ioctl, init/destroy, and newer operations like copy_file_range and lseek.

Special cases match libfuse behavior where missing open/release/opendir/releasedir/statfs are treated as success. Readdir has nested shims to translate old `getdir` callbacks and FUSE 2.x fillers to the FUSE 3.0 filler shape. Statfs conversion handles old `fuse_statfs`, Linux `statfs`, and modern `statvfs`.

Risks: the large version switch matrix is easy to desynchronize. `dt_to_mode` maps `DT_DIR` to `S_IFCHR`, which appears wrong. Several late-operation switches omit version 21 in unsupported-version cases, so a FUSE 2.1 operation could fall into `UNKNOWN_VERSION` rather than returning `-ENOSYS`. Callback prototype and operation-table layout stability are the central correctness constraints.

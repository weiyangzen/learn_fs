# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_SAUNAFS/context_wrap.c

This file is a thin credential/context adapter around the SaunaFS C API. Each wrapper creates a `sau_context_t` from the current Ganesha user credentials, invokes one `sau_*` operation, and destroys the context with GCC cleanup attributes where used.

The wrappers cover lookup, mknod, open, read, write, flush, getattr, opendir/readdir, mkdir, rmdir, unlink, setattr, fsync, rename, symlink, readlink, link, chunk-info retrieval, ACL get/set, byte-range locks, and xattr get/set/list/remove. Inputs are `sau_t *instance`, optional `struct user_cred *cred`, inodes, names, stat data, `fileinfo_t`, or SaunaFS-specific structs. Most functions return the underlying integer status or pointer; context creation failure returns `-1` or `NULL`.

Control flow is deliberately uniform: `createContext(instance, cred)`, null check, call the matching `sau_*` API. This keeps handle/export/ds code independent of raw context management. One notable inconsistency is `saunafs_getlock`, which creates a context without the cleanup attribute, so its context lifetime depends on external behavior or is a leak risk.

State is not persisted here. The context is temporary per operation and the persistent state lives in SaunaFS metadata/data servers and in `sau_fileinfo_t` objects returned from open/opendir.

Dependencies are `context_wrap.h`, `saunafs_internal.h`, and the SaunaFS C API. Integration points are almost every SaunaFS FSAL operation in `handle.c`, `export.c`, `ds.c`, and `mds_handle.c`.

Risks include context allocation failures being collapsed to generic errors, the `saunafs_getlock` cleanup asymmetry, and wrapper signatures that sometimes allow `cred == NULL` for pNFS data-server operations. Test signals should mock or integration-test context creation failure, credential propagation, every wrapper's error mapping via callers, and lock/xattr operations with real SaunaFS servers.

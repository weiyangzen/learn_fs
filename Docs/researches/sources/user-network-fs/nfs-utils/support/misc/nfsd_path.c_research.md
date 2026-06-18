# sources/user-network-fs/nfs-utils/support/misc/nfsd_path.c

## Purpose
Implements `exports.rootdir` aware wrappers for filesystem operations, optionally offloading work to a chrooted worker queue and applying NFS user credentials for open calls.

## Important APIs, Types, and Functions
Functions include rootdir strip/prepend/get/init, stat/lstat/statfs/realpath wrappers, `nfsd_cred_openat()`, read/write wrappers, and `nfsd_name_to_handle_at()` with ENOSYS fallback.

## Control Flow
Initialization reads `exports.rootdir` from config and creates a worker queue chrooted there. Wrapper calls package arguments into small task structs and run them on the worker when present; otherwise they call libc/syscalls directly. Credential open swaps effective credentials around `openat()` and restores them.

## State and Persistence Behavior
Global `nfsd_wq` owns optional worker state. Configured rootdir comes from persistent config. File descriptors, errno, metadata, and read/write side effects are visible to callers.

## Dependencies and Integration Points
Depends on `conffile.h`, `workqueue.h`, `nfs_ucred.h`, `xstat.h`, `nfslib.h`, and system stat/open/read/write/name_to_handle APIs. Used by export realpath, export tests, and cache/filehandle code.

## Risks and Edge Cases
Workqueue setup failure silently falls back to host namespace operations. `nfsd_path_statfs()` casts `struct statfs *` through `struct stat *` function types. Credential swapping must be serialized to avoid thread-wide side effects. `nfsd_path_strip_root()` returns an interior pointer.

## Test Signals
Test rootdir unset, rootdir `/`, duplicate slash/dot stripping, chrooted stat/open/read/write, credential open success/failure/restore, realpath stripping/prepending, statfs behavior, and name_to_handle_at fallback.

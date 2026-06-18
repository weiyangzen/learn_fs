# sources/user-network-fs/nfs-utils/support/include/nfsd_path.h

## Purpose
Declares chroot/rootdir-aware filesystem wrappers used by nfsd export support.

## Important APIs, Types, and Functions
APIs include `nfsd_path_init()`, rootdir get/strip/prepend helpers, stat/lstat/statfs/realpath, credential-aware `openat`, read/write wrappers, `nfsd_name_to_handle_at()`, and inline `nfsd_openat()`.

## Control Flow
When `exports.rootdir` is configured, implementation uses a worker chrooted into that rootdir to run filesystem calls. Otherwise wrappers call system APIs directly.

## State and Persistence Behavior
The implementation owns a process-global workqueue. Filesystem effects and file descriptors are caller-visible; rootdir configuration persists in config file state.

## Dependencies and Integration Points
Used by export realpath, cache channel writes, filehandle lookup, and export path validation. Depends on `nfs_ucred` and workqueue support.

## Risks and Edge Cases
Chrooted workers and credential swaps are sensitive to threading and errno propagation. `strip_root()` returns interior pointers or NULL.

## Test Signals
Test rootdir unset/set, stat/lstat/statfs/realpath under chroot, credential open failures, read/write errno, and name_to_handle_at fallback.

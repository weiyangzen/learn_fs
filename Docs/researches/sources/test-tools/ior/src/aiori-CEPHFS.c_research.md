# sources/test-tools/ior/src/aiori-CEPHFS.c

## Purpose
Implements the IOR `CEPHFS` backend using libcephfs. It exposes file I/O, metadata operations, statfs, sync, and mdtest support through a single `ior_aiori_t cephfs_aiori` registration.

## Important APIs, Types, and Functions
- `struct cephfs_options` holds cluster user, config file, local prefix, remote mount prefix, and lazy-I/O flag. A static instance backs `option_help options`.
- Global `struct ceph_mount_info *cmount` is the mounted CephFS session shared by all callbacks in the process.
- `CEPHFS_Init` creates the mount handle, reads the Ceph config, mounts the remote prefix, and validates root lookup.
- `CEPHFS_Open` maps IOR flags to Ceph flags, strips the configured local prefix with `pfix`, opens via `ceph_open`, and optionally enables `ceph_lazyio`.
- `CEPHFS_Xfer` uses positional `ceph_write` and `ceph_read`; `CEPHFS_Fsync` uses `ceph_fsync`; `CEPHFS_Sync` uses `ceph_sync_fs`.
- Metadata callbacks use `ceph_stat`, `ceph_statfs`, `ceph_mkdir`, `ceph_rmdir`, and `ceph_unlink`.

## Control Flow
IOR calls `.get_options`, `.initialize`, `.xfer_hints`, then create/open, transfer, close/remove, and finalize callbacks. `CEPHFS_Create` delegates to `CEPHFS_Open` with `IOR_CREAT`. Transfers return the requested length after checking for negative or short backend results. `GetFileSize` stat results are reconciled across MPI ranks using sum for file-per-process and min/max consistency checking for shared-file runs.

## State and Persistence
CephFS durability depends on the remote Ceph cluster and explicit `ceph_fsync`/`ceph_sync_fs`. `cmount`, the option singleton, and `hints` are process-global. File handles are heap-allocated `int *` values freed in close.

## Dependencies and Integration Points
Requires `<cephfs/libcephfs.h>`, MPI collectives through IOR utilities, and IOR globals such as `rank`, `testComm`, and `hints`. `enable_mdtest = true` means metadata benchmark paths exercise directory/stat/access callbacks.

## Risks and Edge Cases
- `CEPHFS_Init` warns and returns if options are not populated, so later callbacks can dereference an unmounted `cmount`.
- `pfix` assumes `o.prefix` is non-null and strips it by byte prefix, not path component.
- `CEPHFS_ERR` sets `errno = -ret` and calls fatal IOR error handling; use after already positive `EINVAL` values can set a negative errno.
- Append and direct I/O are explicitly unsupported.
- Lazy I/O changes persistence semantics and only logs a warning if enabling it fails.

## Test Signals
Exercise initialization with missing and valid Ceph options, prefix stripping, N-N and N-1 file-size paths, short-read/short-write failures, `fsyncPerWrite`, lazy I/O, and mdtest operations for mkdir/rmdir/stat/statfs/access.

# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_common.c

## Purpose

`nfs_common.c` is the loadable-module wrapper and common client support file for illumos NFS. It registers the NFS syscall, NFS dynamic root filesystem, NFSv2 client filesystem, NFSv3 client filesystem, and NFSv4 filesystem linkage. It also provides root-mount fallback logic, transfer-size helpers, mount option updates, and the direct-I/O toggle.

## Main Interfaces

Module entry points:

- `_init`
- `_fini`
- `_info`

Dynamic root filesystem:

- `nfsdyninit`
- `nfsdyn_mountroot`

Common sizing and option helpers:

- `nfstsize`
- `nfs3tsize`
- `nfs3_tsize`
- `rfs3_tsize`
- `nfs_setopts`
- `nfs_directio`

The file defines module linkage for:

- `nfssys`
- `nfsdyn`
- `nfs`
- `nfs3`
- externally supplied `modlfs4`

## Module Initialization

`_init()` calls `nfs_clntinit()` first. That initializes common NFS client state, VFS state, NFSv4 client state, and NFS command-door state. It then creates `nfsstat_zone_key` and installs all module linkages.

If installation fails, `_init()` deletes the stats zone key, calls `nfs_clntfini()`, and explicitly runs cleanup for NFSv4, NFSv3, and NFSv2 filesystem registration work that may have been performed indirectly by `mod_install()`.

`_fini()` always returns `EBUSY`, preventing unload.

## Dynamic NFS Root Mount

The pseudo filesystem `nfsdyn` exists only for diskless boot root mounting. `nfsdyn_mountroot()` tries to mount the root filesystem as NFSv4 first, then falls back to NFSv3, then NFSv2 if the previous attempt fails with `EPROTONOSUPPORT`.

For each attempt it:

1. Sets the VFS operations to the candidate NFS version.
2. Fills `struct nfs_args` with server address, filehandle storage, netconfig storage, and hostname storage.
3. Calls `mount_root()` with the requested version.
4. On non-version-mismatch failure, restores `nfsdyn_vfsops`, frees temporary state, and returns the error.
5. On success, frees temporary state and calls the real `VFS_MOUNTROOT()` through the selected filesystem operations.

`ROOT_REMOUNT` is treated as a panic condition; `ROOT_UNMOUNT` is a no-op.

## Transfer Size Helpers

`nfstsize()` returns `NFS_MAXDATA` for NFSv2.

`nfs3tsize()` returns a global maximum NFSv3 transfer size, defaulting to 1 MiB.

`nfs3_tsize()` chooses an NFSv3 client transfer size by transport semantics:

- connection-oriented transports: 1 MiB
- RDMA: 1 MiB
- connectionless transports: 32 KiB

`rfs3_tsize()` performs the equivalent server-side calculation from `svc_req` transport type.

## Mount Option Updates

`nfs_setopts()` updates a live mount’s `mntinfo_t` from `struct nfs_args`. It handles flags and parameters including:

- `NFSMNT_NOAC`
- `NFSMNT_NOCTO`
- `NFSMNT_LLOCK`
- `NFSMNT_GRPID`
- `NFSMNT_RETRANS`
- `NFSMNT_TIMEO`
- `NFSMNT_RSIZE`
- `NFSMNT_WSIZE`
- attribute cache min/max values
- `NFSMNT_LOOPBACK`

Invalid negative retrans values, nonpositive timeouts, and nonpositive read/write sizes return `EINVAL`. Attribute-cache values are clamped to configured maximums and converted from seconds to high-resolution time units.

When `NOAC` is enabled, the root vnode attribute cache is purged.

## Direct I/O

`nfs_directio()` toggles per-rnode direct I/O through `RDIRECTIO`.

When enabling direct I/O, it takes the vnode write lock to avoid racing an active cached write. If dirty cached data or async writes exist, it flushes and invalidates the page cache with `VOP_PUTPAGE(B_INVAL)`. ENOSPC and EDQUOT errors are stored in `rp->r_error` if no previous async write error is recorded.

Disabling direct I/O simply clears `RDIRECTIO`.

## Notable Invariants

- The NFS module is not unloadable after initialization.
- `nfsdyn` is only a bootstrap shim; successful root mounting replaces the VFS ops with the real NFS version.
- NFSv4 root is attempted before NFSv3 and NFSv2, but fallback only happens for protocol-version unsupported cases.
- Direct I/O enablement must flush dirty cached pages while holding the vnode write lock.
- Runtime mount option updates clamp attribute-cache timers and transfer sizes rather than blindly replacing limits.

## Dependencies

This file depends on:

- NFS client initialization/finalization from `nfs_client.c`
- NFSv2, NFSv3, and NFSv4 VFS init/fini and VFS ops
- Boot-time `mount_root()` support from `nfs_dlinet.c`
- VFS module registration APIs
- NFS mount argument definitions
- Rnode and mntinfo state from `nfs_clnt.h` and `rnode.h`

## Research Notes

This file is mostly module and mount plumbing, but `nfsdyn_mountroot()` is important for diskless boot behavior and `nfs_directio()` is important for cache correctness. The highest-risk logic is cleanup after partial module installation failure and the transition from cached I/O to direct I/O while writes may be dirty or outstanding.

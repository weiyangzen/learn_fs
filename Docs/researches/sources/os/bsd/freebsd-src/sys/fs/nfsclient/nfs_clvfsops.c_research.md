# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs_clvfsops.c

## Purpose
Implements FreeBSD's new NFS client VFS operation layer for the `nfs` filesystem type. It handles mount option parsing, diskless root mounting, mount object construction, NFSv4 client/session setup, root vnode creation, statfs/fsinfo refresh, unmount cleanup, mount sync, VFS sysctl handling, forced dismount purge, NLM information extraction, and mount-option reporting.

## Main Interfaces
- Registers `nfs_vfsops` through `VFS_SET(nfs_vfsops, nfs, VFCF_NETWORK | VFCF_SBDRY)`.
- Exports `newnfs_iosize()` to clamp negotiated read/write/readdir sizes and update `f_iosize`.
- Exports `ncl_fsinfo()` for NFSv3 FSINFO probing and mount transfer-size loading.
- Exports `nfscl_retopts()` to format active mount options for user-visible reporting.
- Implements VFS operations: `nfs_mount`, `nfs_cmount`, `nfs_unmount`, `nfs_root`, `nfs_statfs`, `nfs_sync`, `nfs_sysctl`, and `nfs_purge`.

## Key Behavior
- Mount option parsing supports both legacy `nfs_args` and string options, including protocol version, TCP/UDP, cache timeouts, readahead, commit size, Kerberos security flavors, NFSv4 minor version, pNFS, `oneopenown`, TLS, `syskrb5`, and Linux-compatible `nconnect`.
- `mountnfs()` allocates and initializes `struct nfsmount`, copies variable-length Kerberos/mount-path/server-principal strings into trailing storage, initializes socket request state, connects to the server, obtains NFSv4 client/session state when needed, resolves NFSv4 path-based mounts, instantiates the root vnode, loads root attributes/fsinfo, marks ACL/named-attribute support, and enables extra TCP connections after a successful mount.
- NFSv4 path mounts can start with `nm_fhsize == 0`; `nfsrpc_getdirpath()` later fills the root file handle. `syskrb5` may use a fake root file handle until security negotiation allows real lookup.
- `nfs_statfs()` obtains the root vnode, refreshes NFSv3 FSINFO when missing, runs `nfsrpc_statfs()`, loads root attributes, updates mount fsinfo/statfs data, maps NFSv4 errors, and falls back to cached `mnt_stat` for fake-root `WRONGSEC` cases.
- `nfs_mountroot()` configures diskless network state, optional default route, diskless mount arguments, root hostname, and initial time-of-day before calling the same `mountnfs()` path.
- `nfs_unmount()` handles forced and normal unmount differently: forced unmount cancels outstanding RPCs and stops renewal early; successful teardown flushes vnodes, clears nfsiod ownership, waits for forced-dismount RPC cancellation, disconnects MDS/DS sessions, destroys auth/locks, releases credentials, and frees forced-unmount delegations.
- `nfs_sync()` walks dirty vnodes and calls `VOP_FSYNC`, but exits early for lazy syncs and forced dismounts.
- `nfs_sysctl()` exposes VFS query timeout state and tunable console timeout delay.

## Important State
- Allocates `M_NEWNFSREQ` and `M_NEWNFSMNT` memory types.
- Uses global diskless structures `nfs_diskless`, `nfsv3_diskless`, and `nfs_diskless_valid` when NFS root support is not compiled elsewhere.
- Per-mount state includes `nm_sockreq`, `nm_sess`, `nm_clp`, `nm_fh`, `nm_fhsize`, `nm_minorvers`, `nm_privflag`, `nm_newflag`, `nm_aconnect`, `nm_maxfilesize`, transfer sizes, attr/name cache timeouts, TLS certificate name, and trailing name/principal storage.
- Sysctls tune IP paranoia/no-connection defaults, server-down message delays, diskless status, and debug behavior when compiled.

## Dependencies
Depends on FreeBSD VFS mount/vnode APIs, kernel sockets/routing, diskless NFS boot data, RPCSEC TLS availability, NFS client RPC helpers, NFSv4 client/session state helpers, pNFS data-server session structures, nfsiod globals, and common NFS mount/socket abstractions from `nfs_mountcommon.h`.

## Risks and Edge Cases
- Mount option validation is security- and protocol-sensitive: `nconnect` and `syskrb5` are restricted to NFSv4.1/4.2, TLS requires kernel TLS RPC support, and mount updates cannot change protocol/security/lock strategy.
- Variable-length `struct nfsmount` trailing storage depends on exact size and offset calculations for Kerberos names, NFSv4 dirpath, and server principal.
- Switching an updated mount from TCP to UDP is explicitly warned as capable of hanging threads with large in-flight RPCs.
- Fake root file handles and `WRONGSEC` fallback intentionally let mounts/statfs proceed before the real root file handle is available.
- Unmount teardown must coordinate VFS vnode flushing, NFSv4 renewal, forced RPC cancellation, nfsiod queues, session lists, auth handles, and delegation structures without leaving `mnt_data` visible too long.

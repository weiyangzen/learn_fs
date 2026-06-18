# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_vfsops.c

## Purpose

`nfs_vfsops.c` implements the VFS-level NFS filesystem operations: mount, root lookup, unmount, statfs/statvfs, sync, mountroot, diskless boot conversion, mount option decoding, and NFS mount structure allocation/freeing.

## Main Contents

- Registers the `nfs` VFS with `VFS_SET(..., VFCF_NETWORK | VFCF_MPSAFE)` and supplies `nfs_mount`, `nfs_unmount`, `nfs_root`, `nfs_statfs`, `nfs_statvfs`, `nfs_sync`, `nfs_init`, and `nfs_uninit`.
- Defines NFS malloc types and global `nfsstats`, plus sysctls for stats, IP paranoia/no-connection defaulting, debug, diskless state, and tunable I/O size.
- `nfs_iosize()` chooses page-aligned transfer sizes based on NFS version and transport.
- `nfs_convert_oargs()` and `nfs_convert_diskless()` translate old NFS mount/diskless structs into current NFSv3-capable forms. Converted loader-provided v2 root/swap handles are forcibly disabled for this snapshot.
- `nfs_statfs()` and `nfs_statvfs()` issue `NFSPROC_FSSTAT`, decode v2/v3 stat structures, and preserve mount-derived fields such as `f_iosize`.
- `nfs_fsinfo()` issues NFSv3 `FSINFO`, adjusts read/write/readdir sizes and maximum file size, marks `NFSSTA_GOTFSINFO`, and updates mount `f_iosize`.
- `nfs_mountroot()` configures network boot state, interface address, optional default gateway, NFSv3 root mount, optional NFS swap vnode, hostname, and root time.
- `nfs_mountdiskless()` allocates a root mount if needed, optionally performs mount RPC file-handle discovery, and calls `mountnfs()`.
- `nfs_decode_args()` normalizes and clamps mount options: v3-only flags, no-connection semantics, timeouts, retransmits, transfer sizes, attribute cache timers, group count, readahead, dead-server threshold, and reserved-port reconnect behavior.
- `nfs_mount()` copies user mount arguments, handles old-argument compatibility when enabled, supports update mounts, copies file handles/paths/hostnames, imports server sockaddr, and calls `mountnfs()`.
- `mountnfs()` allocates `struct nfsmount`, initializes locks/queues/token/object cache, defaults mount parameters, connects UDP mounts, installs vnode ops, obtains the root `nfsnode`, adds the mount to `nfs_mountq`, and starts NFS I/O reader/writer kernel threads.
- `nfs_unmount()` supports forced unmount cancellation, handshakes unmount-in-progress state, flushes vnodes, stops I/O threads, disconnects sockets, removes mount queue entry, and frees mount data when not Kerberos-held.
- `nfs_root()` obtains the root `nfsnode`, fetches FSINFO or attributes, marks the vnode as `VDIR`/`VROOT`, and returns it.
- `nfs_sync()` scans mount vnodes and calls `VOP_FSYNC()` unless lazy sync is requested.

## Notable Details

- NFSv3 is required for `nfs_mountroot()` by explicitly setting `NFSMNT_NFSV3`; root readdirplus is also enabled.
- `mountnfs()` keeps an extra reference on the root vnode to support `..` traversal if the root nfsnode would otherwise be flushed.
- `nfs_decode_args()` avoids changing buffer-cache-sensitive sizes after FSINFO has been obtained.
- Diskless swap is represented by a fake mount and then forced to a regular-file vnode before `swaponvp()`.
- Mounts create dedicated `nfsiod_rx` and `nfsiod_tx` LWKT threads with CPU placement based on CPU count.

## Integration

This file is the VFS anchor for the NFS client. It creates `struct nfsmount` instances consumed by `nfs_socket.c`, `nfs_bio.c`, `nfs_vnops.c`, and `nfsm_subs.c`, and installs vnode operation tables defined in `nfs_vnops.c`.

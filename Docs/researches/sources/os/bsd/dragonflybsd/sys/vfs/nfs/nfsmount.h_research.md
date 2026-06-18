# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsmount.h

## Purpose

`nfsmount.h` defines `struct nfsmount`, the per-mount NFS client state object stored in `mount->mnt_data`, plus mount service thread state and kernel helper declarations.

## Main Contents

- `enum nfssvc_state` tracks NFS I/O service lifecycle: init, waiting, pending, stopping, done.
- `struct nfsmount` stores:
  - mount flags and internal state,
  - receive/transmit locks, I/O threads, and thread states,
  - associated `struct mount` and per-mount nfsnode allocator,
  - root file handle and server sockaddr/socket/protocol data,
  - timeout, retry, RTT, congestion, and dead-server tracking,
  - read/write/readdir transfer sizes and readahead,
  - attribute cache timer bounds,
  - auth handoff fields and Kerberos/write verifier state,
  - UID nickname auth cache hash/LRU lists,
  - async bio and request queues,
  - maximum file size, root credential, and mount token.
- `VFSTONFS(mp)` casts a VFS mount to its NFS mount state.
- Kernel declarations expose `nfs_free_mount()` and `nfs_setvtype()`.

## Notable Details

- The structure is the central synchronization and queueing object for NFS client I/O.
- It carries both socket transport state and VFS/cache policy state.
- Multiple queues split BIOs, transmit requests, receive requests, and pending requests.
- `nm_token` protects mount-local NFS state across vnode, socket, and bio code.

## Integration

Allocated and initialized in `nfs_vfsops.c`; used throughout `nfs_vnops.c`, `nfs_bio.c`, `nfs_socket.c`, `nfs_iod.c`, and marshalling helpers via `VFSTONFS()`.

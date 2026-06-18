# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs.h

## Role

Central NFS internal header for DragonFly’s legacy NFS client/server implementation. It defines tunables, mount argument ABI, mount/status flags, service syscall structures, client request state, server socket/request state, WebNFS helpers, globals, and function prototypes shared across NFS source files.

## Major Definitions

- Tunables for timeouts, retransmits, I/O sizes, readdir size, read-ahead, async BIO limits, uid hash sizes, attribute cache lifetimes, and server write-gather delay.
- `struct nfs_args` defines the user/kernel mount argument ABI with server address, socket/protocol, file handle, flags, I/O sizes, timeout, retransmit, group limit, read-ahead, dead threshold, hostname, and attribute-cache timers.
- `NFSMNT_*` flags configure soft/hard behavior, I/O sizes, timeouts, interruptibility, unconnected sockets, NFSv3, Kerberos, cache/swapcache, read-ahead, reserved ports, readdirplus, and retry/cache timers.
- `NFSSTA_*` flags track runtime mount state such as write verifier, pathconf/fsinfo availability, mountd association, dismount state, send-space warning, and Kerberos auth state.
- `struct nfsd_args`, `struct nfsd_srvargs`, and `struct nfsd_cargs` define `nfssvc()` arguments for server sockets and Kerberos credential exchange.
- `struct nfsstats` records client and server cache/RPC counters when protocol constants are available.
- `struct nfsreq` represents an outstanding client RPC request.
- `struct nfsuid` caches server-side uid/auth mappings.
- `struct nfssvc_sock` represents an NFS server socket, queued raw records, uid hash tables, write-delay lists, and locking/token state.
- `struct nfsd` tracks a server daemon thread and associated authentication/request state.
- `struct nfsrv_descript` describes an NFS server request, including write-gather fields, mbufs, credentials, file handle, reply state, and NFSv3 flags.

## Important Flags and Macros

- `NFS_CMPFH()` compares file handles.
- `NFS_ISV3()` checks mount protocol version.
- `NFS_SRVMAXDATA()` chooses server max data size.
- `NFSINT_SIGMASK()` identifies signals that can interrupt interruptible NFS mounts.
- `NFSIGNORE_SOERROR()` filters ignorable socket errors for datagram sockets.
- `R_*` flags track client request send/timer/soft/intr/socket/async/queue/lock state.
- `SLP_*` flags track server socket receive/disconnect/stream state.
- `ND_*` flags identify server request read/write/check/NFSv3/Kerberos state.
- `NFSW_CONTIG()` and `NFSW_SAMECRED()` support server write gathering.
- WebNFS escape helpers define `%` decoding and native-character handling.
- `NFS_DPF()` provides category-filtered debug printing when `NFS_DEBUG` is enabled.

## API Surface

The header declares broad NFS subsystem APIs, including:

- Initialization and teardown: `nfs_init()`, `nfs_uninit()`, `nfsrv_initcache()`, `nfsrv_destroycache()`, `nfs_nhinit()`, `nfs_nhdestroy()`.
- Client I/O: `nfs_bioread()`, `nfs_vinvalbuf()`, `nfs_readrpc_uio()`, `nfs_writerpc_uio()`, `nfs_commitrpc_uio()`, `nfs_readdirrpc_uio()`, `nfs_readdirplusrpc_uio()`, `nfs_startio()`, `nfs_doio()`, `nfs_asyncio()`, `nfs_asyncok()`.
- RPC/socket handling: `nfs_reply()`, `nfs_send()`, `nfs_connect()`, `nfs_disconnect()`, `nfs_safedisconnect()`, request cancellation, timer, and auth helpers.
- Server request handling for all major NFS procedures: lookup, getattr, setattr, read, write, create, remove, rename, mkdir, rmdir, readdir, readdirplus, symlink, link, fsinfo, pathconf, commit, access, null, and noop.
- Server socket upcalls, receive path, credential mapping, file-handle-to-vnode lookup, public file handle support, write gather, and error mapping.
- IOD thread controls: `nfssvc_iod_reader()`, `nfssvc_iod_writer()`, stop functions, and wakeups.

## Dependencies

Includes vnode, mutex, thread, signal, mbuf, socket, RPC, NFS protocol, mount, and diskless structures through surrounding source files. It is consumed by nearly every NFS client/server implementation file.

## Research Notes

This header is the NFS subsystem contract. It mixes public-ish mount ABI, private client/server state, and cross-file prototypes, so changes here have broad blast radius across NFS VFS, vnode, socket, server, BIO, Kerberos, and diskless boot paths.

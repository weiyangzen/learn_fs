# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_var.h

This is the umbrella prototype header for the shared NFS implementation. It ties together common helpers, client RPC/state, server RPC/state, vnode-port operations, ACL helpers, and KRPC glue.

Key contents:
- Forward-declares many core NFS structures used across client and server code.
- Declares server state APIs from `nfs_nfsdstate.c`, including client/session/stateid, open, lock, delegation, stable storage, and sequence handling.
- Declares server operation handlers from `nfs_nfsdserv.c`.
- Declares server socket/cache APIs.
- Declares common helper APIs from `nfs_commonsubs.c`, including mbuf helpers, NFSv4 attr helpers, lock helpers, id/name cache, UTF-8 checks, socket send locks, IP parsing, and sequence slots.
- Declares client common, RPC, VFS, state, port, bio, node, and callback APIs.
- Declares server vnode-port APIs for file handle conversion, exports, VOP-backed operations, attributes, reads/writes, opens, locks, and root export.
- Declares KRPC connect/request/disconnect APIs and nfsd/nfscbd socket entry points.

Important dependencies:
- This header is a high-fanout contract between the imported common code and the NetBSD-adapted client/server modules.
- Many prototypes use porting typedefs such as `NFSPROC_T`, `vnode_t`, `mount_t`, `NFSACL_T`, and `NFSSOCKADDR_T`.

Risks and notes:
- Because it centralizes prototypes across many compilation units, stale declarations can hide integration drift.
- It documents subsystem boundaries more than it implements behavior.

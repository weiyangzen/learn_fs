# File Research: sources/os/bsd/netbsd-src/sys/kern/uipc_usrreq.c

## Purpose
Implements NetBSD AF_LOCAL/Unix-domain socket protocol operations, including pathname-bound socket nodes, stream/datagram connection management, local credential passing, `SCM_RIGHTS` file-descriptor passing, and garbage collection of file references in transit.

## Main Interfaces
- `uipc_init`: initializes global local-domain lock, sysctl nodes, and the Unix-domain GC thread.
- `unp_attach`, `unp_detach`: allocate/free `unpcb`, reserve buffers, and manage socket locks.
- `unp_bind`: creates a filesystem `VSOCK` node via namei/VOP_CREATE, links `v_socket`, and stores socket path.
- `unp_listen`, `unp_accept`, `unp_connect`, `unp_connect2`, `unp_disconnect`, `unp_shutdown`, `unp_abort`: implement protocol connection lifecycle.
- `unp_send`, `unp_output`, `unp_rcvd`: deliver data/control mbufs and maintain stream backpressure accounting.
- `uipc_ctloutput`: handles `LOCAL_CREDS`, `LOCAL_OCREDS`, `LOCAL_CONNWAIT`, and `LOCAL_PEEREID`.
- `unp_externalize`, `unp_internalize`: convert between user file descriptors and in-kernel `file_t *` arrays for `SCM_RIGHTS`.
- `unp_addsockcred`: appends credential control messages.
- `unp_gc`, `unp_thread`, `unp_scan`, `unp_dispose`, `unp_mark`: mark/sweep garbage collector for cyclic or abandoned file references in socket buffers.
- `unp_usrreqs`: exports protocol operations to the socket layer.

## State And Control Flow
Each socket has an `unpcb` tracking peer/reference links, bound vnode/path, credentials, stream-lock state, and accounting for peer receive-buffer pressure. Datagram sockets use the domain-wide `uipc_lock`; stream sockets start with private locks, may move to `uipc_lock` while listening/connecting, then connected pairs share a private stream lock. Pathname bind creates a `VSOCK` vnode and stores a backpointer in `v_socket`. `SCM_RIGHTS` internalization increments global `unp_rights`, file refcounts, and per-file message counts; externalization allocates recipient descriptors and drops in-flight references.

## Dependencies And Integration
Integrates socket buffers, vnode/namei/VOP_CREATE/VOP_ACCESS, file descriptor tables, process cwd/chroot state, kauth credentials, sysctl, module compatibility hooks for old credentials, file-list scanning, and generic socket protocol dispatch.

## Risks And Edge Cases
- Lock transitions between private stream locks and `uipc_lock` are subtle and explicitly documented as race-sensitive.
- `unp_bind` and `unp_connect` drop the socket lock for pathname operations and use `UNP_BUSY` to reject overlapping operations.
- Passing directory descriptors across chroot boundaries is checked in `unp_externalize` with `vn_isunder`.
- `SCM_RIGHTS` has quota-like limiting via `maxfiles / unp_rights_ratio` and rejects kqueue descriptors.
- Cycles of sockets containing descriptors require the GC thread; correctness depends on `f_count`, `f_msgcount`, `f_unpcount`, `FMARK`, `FDEFER`, and `FSCAN` accounting.

## Filesystem Relevance
High for cross VFS/socket behavior. AF_LOCAL bind/connect uses real filesystem path lookup and `VSOCK` vnodes, while descriptor passing can transport vnode-backed files and must respect chroot visibility.

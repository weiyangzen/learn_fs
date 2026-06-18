# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_syscalls.c

## Purpose

`nfs_syscalls.c` implements DragonFlyBSD's `nfssvc(2)` pseudo-system-call path for NFS server operation and client-side Kerberos/nickname authentication handoff. It is the user/kernel bridge used by `nfsd`, mount helper/client daemon paths, and NFS server socket setup.

## Main Contents

- `sys_nfssvc()` validates restricted-root capability, serializes on `nfs_token`, and dispatches `NFSSVC_*` commands:
  - `NFSSVC_BIOD` is obsolete and returns `ENXIO`.
  - `NFSSVC_MNTD` resolves a mount root vnode and runs `nfs_clientd()` for mount-side auth handling.
  - `NFSSVC_ADDSOCK` imports a socket fd and optional address, then calls `nfssvc_addsock()`.
  - server daemon requests pass auth results/failures into an existing `struct nfsd`, then run `nfssvc_nfsd()`.
- `nfssvc_addsock()` prepares a server socket:
  - reserves large socket buffers, disables socket autosize, clears interrupt timeouts,
  - enables TCP keepalive, `TCP_NODELAY`, and `TCP_FASTKEEP`,
  - allocates `struct nfssvc_sock`, links it into `nfssvc_sockhead`, installs receive upcall, and wakes `nfsd`.
- `nfssvc_nfsd()` is the main kernel NFS daemon loop:
  - creates/links a per-thread `struct nfsd` if needed,
  - finds sockets needing service, drains socket records, handles disconnects,
  - consults the recent-request cache, supports write gathering, executes `nfsrv3_procs[]`,
  - prepends record markers for stream transports, sends replies, logs RTT data, and cleans descriptors.
- `nfsrv_zapsock()` invalidates and shuts down a service socket, clears upcalls, frees raw mbufs, queued records, UID auth cache entries, and gathered write descriptors.
- `nfsrv_slpref()`, `nfsrv_slpderef()`, `nfs_slplock()`, and `nfs_slpunlock()` manage service-socket references and send/receive serialization.
- `nfsrv_init()` initializes or tears down all server socket and daemon queues, including recent-request cache cleanup when terminating.
- `nfsd_rt()` records server-side RTT/performance log entries.
- `nfs_getauth()`, `nfs_getnickauth()`, and `nfs_savenickauth()` implement the client-side Kerberos-style full-auth and nickname-auth cache handoff machinery.

## Notable Details

- The file is compiled with substantial server logic excluded under `NFS_NOSERVER`.
- `sys_nfssvc()` normalizes `EINTR` and `ERESTART` to success on return.
- The server loop intentionally drops `nfs_token` while holding the per-socket token during request processing.
- Privileged source port checks are optional via `vfs.nfs.nfs_privport`.
- Kerberos encryption blocks are stubs under `#ifdef NFSKERB`/`XXX`; non-Kerberos builds use zero timestamp verifier placeholders.
- `nfsrv_zapsock()` increments/decrements references indirectly so sockets are invalidated before final object free, avoiding use-after-free while daemons are active.

## Integration

This file ties server sockets and daemon scheduling to `nfs_socket.c`, request dispatch in `nfs_serv.c`, duplicate-request caching in `nfs_srvcache.c`, marshalling helpers in `nfsm_subs.c`, and mount/auth state in `nfsmount.h`.

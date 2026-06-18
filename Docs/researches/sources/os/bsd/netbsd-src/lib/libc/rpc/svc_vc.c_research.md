# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_vc.c

This file implements libc RPC server-side connection-oriented transports. It supports two SVCXPRT modes: a rendezvous/listener transport created by `svc_vc_create`, and an established stream transport created by `svc_fd_create` or accepted from the rendezvous path.

Main exported entry points are `svc_vc_create`, `svc_fd_create`, and `__svc_clean_idle`. The listener path stores `struct cf_rendezvous` in `xp_p1`, records send/receive sizing and max-record policy, enables `LOCAL_CREDS` for AF_LOCAL sockets, snapshots the local address, installs rendezvous ops, and registers the transport. The established connection path uses `makefd_xprt`, which allocates `struct cf_conn`, creates an `xdrrec` stream over `read_vc`/`write_vc`, sets verifier storage, installs normal RPC ops, discovers `xp_netid`, and registers the transport.

`rendezvous_request` accepts incoming sockets, creates a new transport, copies the peer address, applies TCP_NODELAY when socket metadata is available, inherits rendezvous buffer/max-record settings, and optionally switches the accepted socket to nonblocking mode with `__xdrrec_setnonblock`. It returns `FALSE` because the listener itself never yields an RPC request.

The data path is built around `xdr_rec.c`: `svc_vc_recv` sets decode mode, skips to a record boundary, decodes an RPC call, and saves the transaction id; `svc_vc_reply` sets encode mode, restores the saved xid, serializes the reply, and ends/flushed the record. `svc_vc_getargs` and `svc_vc_freeargs` delegate argument decode/free to the service XDR procedure.

Connection I/O is fatal-on-error. `read_vc` has a blocking mode with a 35-second `pollts` timeout and a nonblocking mode that treats `EAGAIN` as no bytes. For AF_LOCAL sockets it consumes SCM_CREDS on first read and stores copied credentials in `xp_p2`. `write_vc` writes until all bytes are sent, marking the stream dead on hard write errors; nonblocking writes tolerate `EAGAIN` only for about two seconds.

Resource cleanup is centralized in `svc_vc_destroy` and `__svc_vc_dodestroy`, unregistering transports, closing fds, destroying XDR streams, freeing address buffers, transport strings, netids, and transport-private structs. `__svc_clean_idle` scans registered transports under `svc_fd_lock`, selects eligible VC connections, and destroys either those idle past a timeout or the least-active one when `timeout == 0`.

Research notes and risks:
- `svc_fd_create` has a cleanup branch using `rep->xp_ltaddr.maxlen` while the local variable is `ret`; as read, that appears to be a compile-time typo or stale code path.
- Accepted transport error cleanup closes the socket directly rather than destroying a partially built `newxprt`, so allocation failures after `makefd_xprt` can leave registered transport state unless external registration cleanup compensates.
- Nonblocking max-record behavior depends on `xdr_rec.c` full-record assembly and `__svc_clean_idle` for pressure relief.

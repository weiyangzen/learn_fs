# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_dg.h

Read completely: 51 lines.

Private header for datagram service transport state. It defines `struct svc_dg_data`, stored in `SVCXPRT.xp_p2`, containing the IO buffer size, current xid, XDR stream, verifier body storage, and optional duplicate-request cache pointer.

It also defines `__rpcb_get_dg_xidp(x)` so rpcbind-related code can access the datagram xid field. Comments state this header exists only so rpcbind code can include the datagram-private layout.

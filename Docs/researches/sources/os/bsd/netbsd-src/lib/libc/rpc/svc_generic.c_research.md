# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/svc_generic.c

Read completely: 326 lines.

Implements high-level server creation APIs `svc_create()`, `svc_tp_create()`, and `svc_tli_create()`. `svc_create()` iterates transports selected by `__rpc_setconf(nettype)`, reuses existing transports for the same netid from a static `xprtlist`, and registers each program/version with `svc_reg()`.

`svc_tp_create()` creates one transport with `svc_tli_create()`, unsets any old rpcbind mapping, and registers with rpcbind. `svc_tli_create()` opens a socket from netconfig when needed, detects socket info for provided fds, binds to a reserved or anonymous address when unbound, listens for non-datagram transports, then delegates to `svc_fd_create()`/`svc_vc_create()` for streams or `svc_dg_create()` for datagrams.

The created transport gets `xp_type`, `xp_netid`, and `xp_tp` filled from socket/netconfig data. This is the main bridge between netconfig transport selection and concrete service transport implementations.

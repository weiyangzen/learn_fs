# File Research: sources/os/bsd/netbsd-src/lib/libc/rpc/rpc_internal.h

Read completely: 85 lines.

Private libc RPC header declaring internal-only helpers and shared globals. It exposes private XDR-record functions, service transport unregister/idle-cleanup hooks, transport/address conversion helpers, rpcbind lookup helpers, socket/netconfig conversion helpers, `rpc_nullproc()`, `__rpc_sockisbound()`, `__rpc_getxid()`, and `_get_next_token()`.

It also declares service globals (`__svc_xports`, `__svc_maxrec`, `__svc_flags`, `__rpc_lowvers`) and, under `_REENTRANT`, all lock objects defined in `mt_misc.c`.

This is the coordination header for the RPC implementation internals; it is explicitly not an exported public interface.

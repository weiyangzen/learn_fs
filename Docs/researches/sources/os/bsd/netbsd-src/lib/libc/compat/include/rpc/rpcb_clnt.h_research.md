# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/rpc/rpcb_clnt.h

Declares compatibility RPC binder client APIs.

It exposes old `rpcb_rmtcall` using `timeval50`, old `rpcb_gettime` using `int32_t *`, and modern `__rpcb_rmtcall50` / `__rpcb_gettime50` variants.

This preserves RPC time-related ABI.

# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/compat_rpcb.c

Read completely: 83 lines.

This implements compatibility `rpcb_rmtcall` and `rpcb_gettime`. `rpcb_rmtcall` converts a `timeval50` timeout and delegates to `__rpcb_rmtcall50`; `rpcb_gettime` calls `__rpcb_gettime50` and narrows the returned `time_t` to `int32_t`.

Important interactions: provides weak aliases and reference warnings for legacy RPC binder APIs.

Security/reliability notes: `rpcb_gettime` has inherent year-2038 style truncation because the legacy output pointer is `int32_t *`.

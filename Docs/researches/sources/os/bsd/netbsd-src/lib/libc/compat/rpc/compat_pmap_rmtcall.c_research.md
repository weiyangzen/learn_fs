# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/rpc/compat_pmap_rmtcall.c

Read completely: 69 lines.

This implements old `pmap_rmtcall` taking `struct timeval50`. It converts the timeout to current `struct timeval` and forwards all arguments to `__pmap_rmtcall50`.

Important interactions: exposes a weak alias for legacy symbol binding and warns callers to include the current RPC header for the correct reference.

Security/reliability notes: straightforward time conversion wrapper; timeout truncation or widening semantics are delegated to `timeval50_to_timeval`.

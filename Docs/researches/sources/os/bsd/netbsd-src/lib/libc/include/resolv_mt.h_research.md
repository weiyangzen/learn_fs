# File Research: sources/os/bsd/netbsd-src/lib/libc/include/resolv_mt.h

Resolver multi-threading private context header.

Defines:
- `__res_enable_mt` and `__res_disable_mt`.
- `mtctxres_t`, a per-thread resolver context containing private flags and buffers formerly implemented as statics.
- `___mtctxres()` accessor and `mtctxres` macro.
- Macros mapping resolver static buffers like `inet_nsap_ntoa_tmpbuf`, `p_option_nbuf`, and `loc_ntoa_tmpbuf` to fields in the per-thread context.

Used by resolver and NSAP conversion code to avoid shared static buffers.

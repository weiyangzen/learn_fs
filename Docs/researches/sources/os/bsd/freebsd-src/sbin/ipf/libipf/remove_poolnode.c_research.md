# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_poolnode.c

Pool node removal helper.

Key behavior:
- Copies address, mask, info flag, and node name into a local `ip_pool_node_t`.
- Calls `SIOCLOOKUPDELNODE`.
- Reports failures through `ipf_perror_fd()` unless `OPT_DONOTHING`.

Research notes:
- Does not copy TTL/death time because it is irrelevant to deletion.

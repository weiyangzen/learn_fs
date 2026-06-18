# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/remove_pool.c

Pool lookup-table removal helper.

Key behavior:
- Builds an `IPLT_POOL` lookup operation from an `ip_pool_t`.
- Calls `SIOCLOOKUPDELTABLE`.
- Reports failures through `ipf_perror_fd()` unless `OPT_DONOTHING`.

Research notes:
- Includes `ip_htable.h` even though it removes pools.

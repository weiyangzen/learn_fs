# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/load_pool.c

Pool lookup-table loader/remover.

Key behavior:
- Builds `IPLT_POOL` lookup operation from an `ip_pool_t`.
- Supports anonymous pools when the name is empty.
- Adds the table, optionally prints it, loads each node with `load_poolnode()`, and deletes it in remove mode.

Research notes:
- Anonymous table names can be filled back from the kernel-created name.

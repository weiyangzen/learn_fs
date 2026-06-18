# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ippool/ippool.c

This is the `ippool` command-line frontend for managing IPFilter lookup objects: pools, hash tables, group maps, and destination lists.

The `main()` dispatcher selects one command mode from add/remove pool, add/remove node, load file, flush, list, and stats. It also seeds parser variables from `IPPOOL_PREDEFINED`.

`poolnodecommand()` handles single node add/remove operations. It parses role, table type, pool/hash name, TTL, dry-run/debug/verbose flags, and an address or prefix. It then calls `load_poolnode()`, `remove_poolnode()`, `load_hashnode()`, or `remove_hashnode()`.

`poolcommand()` creates or removes whole pool/hash objects. It supports hash seed and type mapping, and when removing with unspecified type it attempts both hash and pool removal.

`loadpoolfile()` opens the lookup device unless dry-run/no-open is active, then delegates declarative parsing to `ippool_parsefile()`.

`poolstats()` and `poolflush()` issue lookup ioctls to fetch object counts or flush objects by role/type. `poollist()` supports live-kernel listing and dead-kernel/core listing. Live listing uses `SIOCLOOKUPSTAT` and `SIOCLOOKUPITER`; dead listing uses `nlist()` and `kmemcpy()` to walk kernel symbols.

`setnodeaddr()` converts command-line IPv4/IPv6 prefixes into either `ip_pool_node_t` or `iphtent_t`, including masks and address-family metadata.

Important dependencies include `ipf.h`, `netinet/ip_lookup.h`, `ip_pool.h`, `ip_htable.h`, `kmem.h`, generated `ippool` parser symbols, and the libipf load/remove/print helpers.

Implementation notes and risks:
- Global state (`opts`, `fd`, `use_inet6`, `pool_fields`) is shared with parser/helper code.
- Option parsing uses repeated `getopt()` in subcommands; callers depend on normal process-style invocation.
- Dead-kernel listing is tightly coupled to kernel symbol names and structure layouts.
- IPv6 address mask handling in `setnodeaddr()` is explicitly marked sloppy by comments.

# File Research: sources/os/bsd/openbsd-src/sbin/unwind/libunbound/iterator/iter_donotq.c

Implementation of iterator do-not-query address filtering.

Core behavior:
- `donotq_create()` allocates structure and regional allocator.
- `donotq_apply_cfg()` clears old regional data, initializes address tree, reads configured `donotqueryaddrs`, optionally adds localhost ranges, and initializes parent pointers.
- `donotq_str_cfg()` parses netblock strings with `netblockstrtoaddr()`.
- `donotq_lookup()` checks if an address matches a blocked span.
- `donotq_get_mem()` reports structure plus regional memory.

Default policy:
- If `cfg->donotquery_localhost` is set, adds `127.0.0.0/8`.
- Adds `::1` as well when IPv6 is enabled.

Role in group:
- Prevents iterator server selection from querying prohibited addresses such as localhost.

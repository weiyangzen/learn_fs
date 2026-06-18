# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ippool/ippool_y.y

This yacc grammar parses declarative `ippool` configuration files. It supports older `table role = type ... { ... }` syntax and newer `pool role/type(name; opts) { ... }` forms.

It builds and loads:
- Tree pools (`ip_pool_t` plus linked `ip_pool_node_t` ranges).
- Hash tables (`iphtable_t` plus linked `iphtent_t` entries).
- Group maps (`IPHASH_GROUPMAP`) with per-entry group assignment.
- Destination lists (`ippool_dst_t` plus `ipf_dstnode_t` entries) with policies such as round-robin, random, hash, source-hash, destination-hash, and weighted connection.

The parser resolves inline addresses, prefix lengths, explicit masks, numeric names, string names, URL/file-backed host lists, and whois-derived ranges. `add_htablehosts()` and `add_poolhosts()` convert host/list sources into hash or pool entry lists using `load_url()`/`gethost()`. `read_whoisfile()` converts parsed whois ranges into pool nodes.

`ippool_parsefile()` and `ippool_parsesome()` set up parser dictionaries, input streams, debug flags, and the ioctl callback. Each parsed object is immediately loaded through `load_pool()`, `load_hash()`, or `load_dstlist()` and temporary linked entries are freed afterward.

Important dependencies include `ippool_l.h`, `ipf.h`, `ip_lookup.h`, `ip_pool.h`, `ip_htable.h`, `ip_dstlist.h`, URL/file loading helpers, whois parsing, and lexer global flags such as `yyexpectaddr`.

Implementation notes and risks:
- Parser state is global and not reentrant.
- Several grammar actions allocate nodes and rely on later manual freeing.
- Some URL/hostname paths use `use_inet6` as implicit global parser state.
- Address parsing mutates input strings when splitting prefixes.

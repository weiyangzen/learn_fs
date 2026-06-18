# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipnat/ipnat.c

`ipnat.c` implements the IPFilter NAT administration command. It loads/removes NAT rules, flushes NAT mappings/rules, and prints NAT statistics, rules, sessions, and hostmaps.

Major behaviors:
- Parses options for clear/flush/debug/file/load/list/match/core/kernel/dry-run/field output/purge/remove/no-resolve/stat/verbose.
- Reads predefined variables from `IPNAT_PREDEFINED`.
- Opens `IPNAT_NAME`, verifies version compatibility, and fetches `natstat_t` through `SIOCGNATS`.
- Supports crash-dump/kernel mode via `openkmem()` and `nlist()` symbol extraction.
- Loads NAT rule files with `ipnat_parsefile(fd, ipnat_addrule, ioctl, file)`.
- Flushes active NAT sessions or NAT rule lists using `SIOCIPFFL`, or expression-matched flushing via `SIOCMATCHFLUSH`.
- Lists NAT rules and active sessions either from live iterators or dead-kernel memory.
- Prints NAT stats, inbound/outbound side counters, hash bucket efficiency/usage/min/max/average lengths, log counters, active counts, flush counters, hostmap counters, and rule counts.
- Verbose listing includes hostmap tables.

Expression filtering:
- `nat_matcharray()` evaluates parsed IPF expressions against `nat_t` objects for protocol, IPv4/IPv6 source/destination addresses, any/source/destination TCP/UDP ports, and negation.
- NAT address matching considers both original and translated source/destination endpoints.

Live/dead split:
- Live mode uses `SIOCGENITER` for NAT rules, NAT sessions, and hostmaps, deleting iterator tokens afterward.
- Dead mode copies `nat_table`, `nat_list`, `maptable`, sizes, and `nat_instances` via kmem symbols.

Notable detail:
- In dead-mode `dotable()`, the kmem copy source for bucket data uses `nsp->ns_nattab_sz` rather than a table pointer, which looks suspicious.

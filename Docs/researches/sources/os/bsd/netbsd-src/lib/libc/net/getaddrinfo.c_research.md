# File Research: sources/os/bsd/netbsd-src/lib/libc/net/getaddrinfo.c

Read completely: 2889 lines.

This file implements `getaddrinfo`, `freeaddrinfo`, `allocaddrinfo`, and `gai_strerror`, plus the resolver/files/NIS backends and address ordering machinery. It supports IPv4 and, when enabled, IPv6, including numeric hosts, scoped IPv6 literals, hosts-file lookups, DNS A/AAAA/SRV queries, optional YP, service-name resolution, `AI_ADDRCONFIG`, `AI_CANONNAME`, `AI_PASSIVE`, `AI_NUMERICHOST`, `AI_NUMERICSERV`, and NetBSD `AI_SRV` behavior.

The top-level `getaddrinfo` validates hints, resolves service constraints, explores NULL/numeric names first, dispatches FQDN lookups through `nsdispatch`, and reorders non-passive nonnumeric results. `explore_null` generates wildcard or loopback addresses; `explore_numeric`/`explore_numeric_scope` parse IPv4, IPv6, and scope IDs; `get_port` resolves numeric/service ports; `get_ai` allocates an `addrinfo` plus inline sockaddr; `_files_getaddrinfo` scans `_PATH_HOSTS`; `_dns_getaddrinfo` queries DNS, trying SRV first when requested.

DNS logic uses `res_target` chains to issue A and AAAA queries, parse answers with `getanswer`, handle CNAMEs, build SRV target lists sorted by priority/weight, and run search-list behavior through `res_searchN`/`res_querydomainN`. Result ordering follows RFC3484-style destination sorting with kernel address-selection policy, source-address probing via UDP `connect`, scope comparisons, deprecated-source checks, policy label/precedence, and longest-prefix matching.

Security/reliability notes: allocation ownership is clear: `allocaddrinfo` places `ai_addr` inline and `freeaddrinfo` frees canon names plus each node. The file is careful about service/numeric validation and many DNS buffer sizes, but DNS answer parsing uses many manual pointer advances; changes should preserve explicit `eom`/RDLENGTH bounds checks. `freeaddrinfo(NULL)` is documented in the source comments as not accepted and would trip the diagnostic assumption/path.

# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dblookup.c

Converts Plan 9 NDB tuples into DNS resource records and maintains database-derived cache/area state for the DNS daemon. It is the bridge between `/lib/ndb`/`/net/ndb` records and `RR` objects from `dns.h`.

`dblookup()` handles class/type filtering, `Tall` expansion, exact/lowercase/wildcard lookups, cached-db mode, owner assignment, and response-code decisions for names outside served areas. `dblookup1()` maps DNS types to NDB attributes and record constructors, including A/AAAA, CNAME, MX, NS, PTR, SOA, SRV, NULL, TXT, and AXFR/IXFR stubs.

Record constructors parse tuple attributes into typed RR payloads. SOA construction derives serials from database mtimes unless overridden, fills timers, builds mailbox names, and attaches `dnsslave` servers for notification.

Database caching is handled by `db2cache()`, `dbfile2cache()`, `dbtuple2cache()`, and `dbpair2cache()`. Reloads compare backing-file mtimes, reopen changed NDBs, rebuild owned/delegated areas, refresh straddle-server configuration, age old DB records, mark authoritative records in served zones, and synthesize reverse PTRs.

Resolver support includes `dnsservers()` and `domainlist()` from `@dns`/`dnsdomain` NDB data, rejection of local/self DNS servers, bad-delegation detection, inside/outside namespace selection for straddling servers, and local synthetic DNS server records.

Reverse PTR synthesis covers IPv4 `in-addr.arpa`, RFC2317 classless delegation, and IPv6 `ip6.arpa` nibble domains. Risks include extensive global state under `dblock`/`dnlock`, mutable static cached tuples for local DNS configuration, special-case straddle logic, and partially implemented AXFR/IXFR handling.

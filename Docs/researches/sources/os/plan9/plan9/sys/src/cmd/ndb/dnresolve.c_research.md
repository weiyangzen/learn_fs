# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnresolve.c

Full recursive resolver implementation for RFC1035/RFC1123-style DNS queries. It coordinates cache lookups, CNAME chasing, nameserver discovery, UDP/TCP transport, retry timing, negative caching, delegation processing, and straddling inside/outside network behavior.

`dnresolve()` handles search domains for unrooted single-label names, recursion-depth protection, direct lookup, CNAME retries, status propagation, and answer randomization. `dnresolve1()` checks cache/database authority before issuing external queries through a heap-allocated `Query`.

`Query` and `Dest` are carefully allocated off-stack because `slave()` forks shared-memory workers and stack-local locks/arrays would diverge. Resolver transport uses `udpport()`, `mkreq()`, `readnet()`, `readreply()`, `mydnsquery()`, `xmitquery()`, `tcpquery()`, and `queryns()`. UDP replies with `Ftrunc` trigger TCP retry.

Nameserver selection uses cached A/AAAA, DB hints, recursive lookup of nameserver addresses, multicast/self-address rejection, and inside/outside filtering for straddling servers. `netquery()` limits duplicate concurrent queries per `(domain,type)` with per-DN locks and `Maxoutstanding`.

`procansw()` incorporates answer, authority, and additional RRs into cache, handles bad delegations, strips SOA from authority for negative-cache processing, recurses on better NS referrals, and caches negative responses via `cacheneg()`.

Wait times are weighted by estimated likelihood of RR existence to reduce delays for low-probability CNAME/AAAA queries. Risks include many interleaved ownership transfers of RR lists, global stats mutation, timeouts via `alarm`, and correctness reliance on Plan 9 network “headers” UDP format.

# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnresolve.c

Implements recursive DNS resolution and outbound DNS transport.

Key elements:
- Public entry point `dnresolve` resolves `(name, class, type)` with optional recursion, CNAME chasing, search-domain expansion, and negative response reporting.
- `dnresolve1` checks cache/database, local authoritative areas, then performs network lookup through `issuequery`.
- `issuequery` chooses configured resolver servers, local authoritative NS entries, cached NS entries, or database NS hints while walking up the DNS tree.
- `netquery`, `doquery`, `udpqueryns`, `tcpquery`, and `tlsqueryns` implement outbound DNS over UDP, TCP, and TLS.
- `mkreq` builds DNS query packets, including EDNS options from `mkednsopt`.
- `readreply` validates response ID, question owner, and query type, and detects truncation.
- `procansw` validates and incorporates answer, authority, and additional sections into the cache.
- `serveraddrs` finds or resolves nameserver A/AAAA addresses while avoiding multicast/broadcast, self-addresses, and recursive loops.
- `cacheneg` stores negative responses with SOA-derived TTL when available.

Notable behavior:
- EDNS advertised UDP payload is conservatively set to 1232 bytes for IPv6 MTU safety.
- TCP connections are cached briefly and reused for up to `Maxtcpresuetm`.
- DNS-over-TLS is selected for synthetic `local#dot#server` or `override#dot#server` NS owner names and validates certificates against `/sys/lib/tls/dns`.
- Bad delegations and out-of-bailiwick SOA/NS/hints are filtered before cache insertion.
- Resolver recursion depth is capped at 12.
- For 9P-originated requests, `netquery` calls `slave` and avoids blocking the 9P loop when no worker can be created.

Risks and quirks:
- Negative responses need not be authoritative before caching; this is intentional per comments but broadens cache trust.
- `procansw` aggressively filters answer owner/type, which keeps cache safer but may discard uncommon DNS response shapes.
- Timeout behavior is tuned around `Maxreqtm`, `Minreqtm`, and exponential UDP retransmits.

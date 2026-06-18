# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dns.c

Main `ndb/dns` service: a mounted 9P DNS query file plus optional UDP/TCP DNS server.

Key elements:
- Parses service flags for resolver mode, forwarding-only mode, serving mode, recursion policy, cache target, database file, certificate, and network mount point.
- Initializes DNS cache/database, creates `/srv/dns...`, mounts a synthetic 9P service at the selected net mount point, and optionally starts UDP/TCP/TLS DNS servers.
- Exposes a single file named `dns` under the mounted directory.
- Handles 9P fids with `Mfile`, active requests with `Job`, and dispatches 9P messages in `io`.
- `rwrite` accepts queries in `domain type` form and owner-only commands `debug`, `refresh`, and `target N`.
- `lookupquery` calls `dnresolve`, strips negative RR objects, and formats replies.
- `respond` stores formatted `%R` or `%Q` records in the fid buffer for later reads.
- Provides shared debug logging hooks `logreply`, `logrequest`, and `getdnsservers`.

Notable behavior:
- Writes must be at offset zero and under `Maxrequest`.
- Prefixing the query with `!` switches output to attribute-value `%Q` format.
- A trailing dot on the requested name marks it as rooted.
- Each query increments DNS stats and participates in `getactivity`/`putactivity`.

Risks and quirks:
- The service hand-rolls a small 9P loop instead of using lib9p.
- Per-fid reply buffers are fixed size (`Maxreply`) with a fixed maximum RR offset table.
- Owner-only commands are gated by the fid user matching the DNS server’s startup user.

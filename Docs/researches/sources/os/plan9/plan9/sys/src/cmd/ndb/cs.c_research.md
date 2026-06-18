# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/cs.c

Implements Plan 9’s 9P connection server mounted as `/net/cs`. Clients write dial strings or generic NDB queries to the single `cs` file and read back translated clone paths such as `/net/tcp/clone host!port`.

Key structures are `Mfile` for per-fid request/reply state, `Job` for active 9P messages and flush tracking, and `Network` for network-specific lookup/translation hooks. Built-in networks include `tcp`, `udp`, `icmp`, `icmpv6`, `rudp`, `ssh`, and `telco`.

Main flow: `main()` initializes NDB state and mounted networks, `mountinit()` publishes `#s/cs...`, `io()` dispatches 9P requests, `rwrite()` parses commands or dial strings, `lookup()` tries default or explicit networks, and `rread()` streams cached replies. DNS lookups are delegated through `dnsquery()` with slave processes so blocking DNS does not stall the 9P loop.

NDB integration includes `/lib/ndb` plus `/net/ndb`; `ipid()` derives `sysname` from environment, DHCP-provided `/net/ndb`, local IP, or ethernet address. `iplookup()` resolves service names, direct IPs, `$attr` expansions, DNS names, local database entries, and interface-local address ordering. `genquery()` handles `!attr=val...` and `!ipinfo...` queries.

Notable risks and maintenance points: fixed-size request/reply buffers cap responses; `rwrite()` mutates request data in place; concurrency uses Plan 9 `rfork(RFMEM)` plus `setjmp`/`longjmp`, so shared global state and locks are delicate. Some IPv6 behavior is bolted onto IPv4-era paths, and reverse-query convenience code lives elsewhere.

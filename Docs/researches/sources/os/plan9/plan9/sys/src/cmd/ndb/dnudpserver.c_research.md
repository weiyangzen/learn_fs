# File Research: sources/os/plan9/plan9/sys/src/cmd/ndb/dnudpserver.c

UDP DNS server loop for external DNS requests. It announces UDP port 53 in Plan 9 “headers” mode, parses incoming DNS packets, suppresses client retransmissions, dispatches query/notify operations, and writes replies back with UDP headers.

`clientrxmit()` records in-progress `(client header, id, owner, type)` tuples to ignore duplicate retransmissions while a request is active. `dnudpserver()` forks a shared-memory child, loops reading UDP packets with timeout, validates questions/opcodes, sets `Request` metadata, and calls `dnserver()` or `dnnotify()` per question.

Forwarding targets configured by `-T` in `dns.c` are stored as `Forwtarg` entries. `redistrib()` copies incoming packets to these debugging/forwarding UDP targets, redialing failed ports periodically.

`reply()` serializes the DNS response into the UDP payload with `Maxdnspayload` limit and writes it through the original header. Risks include shared global `inprog` without locks because the loop is single-threaded until slave forking, fixed-size forwarding packet buffer, and duplicated activity/fork lifecycle complexity.

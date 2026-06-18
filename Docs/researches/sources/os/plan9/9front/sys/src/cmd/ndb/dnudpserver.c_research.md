# File Research: sources/os/plan9/9front/sys/src/cmd/ndb/dnudpserver.c

UDP DNS server implementation.

Key elements:
- `dnudpserver` forks a UDP server process, announces UDP port 53, and loops reading packet-header mode datagrams.
- Uses `clientrxmit` to suppress exact duplicate retransmissions while a request is in progress.
- Converts packets with `convM2DNS`, validates question count/opcode, and supports query and notify opcodes.
- Handles EDNS request options and sets response size limit accordingly.
- For each question, dispatches to `dnnotify` for NOTIFY or `dnserver` for normal queries.
- `reply` converts `DNSmsg` to wire format and writes it back through the same UDP packet buffer.
- `udpannounce` configures Plan 9 UDP packet headers and ignores ICMP advice.

Notable behavior:
- Maintains `inprog[Maxactive+2]` for retransmission suppression.
- Updates UDP receive stats and participates in global request activity tracking.
- Restarts UDP announce loop if reads fail with too-short data.

Risks and quirks:
- The duplicate suppression key includes raw `Udphdr`, owner pointer, type, and ID.
- Multiple-question packets are processed by looping over `reqmsg.qd`.

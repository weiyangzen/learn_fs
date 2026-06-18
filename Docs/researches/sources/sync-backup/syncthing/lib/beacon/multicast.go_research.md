# sources/sync-backup/syncthing/lib/beacon/multicast.go

Purpose: IPv6 multicast beacon implementation for local discovery.

Important APIs/types/functions: `NewMulticast(addr string)` creates a `cast` with multicast reader and writer. `writeMulticasts` sends payloads to an IPv6 multicast group on each eligible interface with hop limit 1. `readMulticasts` joins the multicast group on eligible interfaces and forwards received datagrams.

Control flow: Writer resolves the UDP6 multicast address, opens a packet connection, sets an IPv6 control message with hop limit 1 and per-interface index, enumerates running multicast-capable interfaces, skips Android point-to-point cellular interfaces, writes to each interface with one-second deadlines, and returns if no sends succeed. Reader resolves and listens on the group address, joins the group on each eligible interface, errors if none joined, then reads datagrams, copies them, and non-blockingly sends to outbox.

State and persistence behavior: Network socket state only. No persistence.

Dependencies and integration points: Depends on `golang.org/x/net/ipv6`, `netutil`, build flags, slog logging, and the common `cast` abstraction. Used by local discovery for IPv6 LAN advertisements.

Risks: IPv6 multicast behavior is platform and interface dependent. `joined` increments even when `JoinGroup` fails, so a system with eligible interfaces but failed joins may proceed and then never receive packets. Outbox full conditions drop messages.

Test signals: No direct tests in this subset. Multicast network behavior is likely covered only by integration/manual testing.

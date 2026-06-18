# sources/sync-backup/syncthing/lib/beacon/broadcast.go

Purpose: IPv4 UDP broadcast beacon implementation for local discovery.

Important APIs/types/functions: `NewBroadcast(port int)` creates a `cast` with broadcast reader and writer. `writeBroadcasts` sends inbound payloads to interface-specific broadcast addresses or global `255.255.255.255`. `readBroadcasts` listens on a UDP4 port and forwards received payloads. `bcast` computes the broadcast IP for an `IPNet`.

Control flow: Writer opens an ephemeral UDP4 socket, closes it on context cancellation, reads payloads from inbox, enumerates running broadcast-capable interfaces, skips Android point-to-point cellular interfaces, computes destinations from global-unicast IPv4 addresses, writes with one-second deadlines, and returns an error if no writes succeed. Reader binds the port, reads into a 64 KiB buffer, copies each datagram, and non-blockingly sends to outbox, dropping when full.

State and persistence behavior: Network sockets and transient datagrams only. No persistence.

Dependencies and integration points: Uses `netutil.Interfaces`, `netutil.InterfaceAddrsByInterface`, build flags for Android behavior, slogutil logging, and the common cast interface. Used by local discovery.

Risks: Broadcast availability varies by OS/interface/firewall. Writer returns the last error when all sends fail, which may be nil in some no-destination paths after fallback. Dropping messages when outbox is full is intentional but can lose discovery packets.

Test signals: `broadcast_test.go` validates `bcast` for multiple CIDR masks. Network send/read behavior is not directly exercised.

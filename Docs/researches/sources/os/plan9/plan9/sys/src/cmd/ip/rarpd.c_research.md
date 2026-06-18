# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/rarpd.c

Reverse ARP daemon for Plan 9 network boot support.

Key behavior:
- Opens NDB, Ethernet RARP packet stream, local IP, local Ethernet address, and optional `/net/arp`.
- Daemonizes, then reads RARP packets.
- Validates packet size and request opcode.
- Looks up target Ethernet address in NDB to obtain the client IP.
- Converts request into RARP reply, fills server hardware/protocol address, and writes a 60-byte Ethernet frame.
- Optionally updates the local ARP table with the client Ethernet/IP mapping.

Integration:
- Uses NDB lookup through `ndbipinfo()`.
- Uses EtherType `0x8035`.
- Uses Plan 9 network mount selected by `-x`.

Risks and notes:
- The packet opcode check uses byte-level logic for RARP request/reply.
- `lookup()` has a static local `Ndb *db` that shadows the global `db`, reopening the default database instead of using the configured one.

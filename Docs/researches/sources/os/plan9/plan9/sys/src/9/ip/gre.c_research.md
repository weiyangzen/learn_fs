# File Research: sources/os/plan9/plan9/sys/src/9/ip/gre.c

Implements Generic Routing Encapsulation over IPv4.

Key responsibilities:
- Registers protocol `gre` for IP protocol number 47.
- `greconnect` uses standard IP connect parsing, then rejects duplicate remote address/protocol conversations.
- `grecreate` sets up a packet read queue and bypass write path.
- `grekick` builds outgoing IPv4/GRE packets, supports raw and cooked modes, fills source/destination addresses and encapsulated protocol, and sends through `ipoput4`.
- `greiput` receives GRE packets, normalizes block lists, parses optional checksum/routing/key/sequence fields, matches forwarding retunnel sessions first, then raw/conversation sessions, trims IP header, and queues payload.
- Supports specialized retunneling state: home address, north/south endpoints, care-of address, sequence numbers, downlink/uplink suspension, uplink key, pending and buffered ring queues.
- Control commands include `raw`, `cooked`, `retunnel`, `report`, `dlsuspend`, `ulsuspend`, `dlresume`, `ulresume`, `forward`, and `ulkey`.
- `grestats` reports packet and byte counters plus length errors.

Notable behavior:
- Uses bounded power-of-two rings for pending/buffered retunnel packets and drops oldest entries on overflow.
- Avoids forwarding while holding retunnel locks where possible, at the cost of explicit race handling.

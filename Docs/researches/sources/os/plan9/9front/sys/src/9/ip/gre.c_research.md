# File Research: sources/os/plan9/9front/sys/src/9/ip/gre.c

Implements Generic Routing Encapsulation over IPv4, including normal raw/cooked GRE conversations and specialized retunneling/forwarding support with buffering and sequence tracking.

Key responsibilities:
- Registers protocol `gre` for IP protocol number 47.
- Connects GRE conversations with `greconnect()`.
- Encapsulates outbound GRE packets in `grekick()`.
- Receives and demultiplexes GRE packets in `greiput()`.
- Supports control commands: `raw`, `cooked`, `retunnel`, `report`, `dlsuspend`, `ulsuspend`, `dlresume`, `ulresume`, `forward`, and `ulkey`.
- Tracks GRE packet/byte counters and short-packet errors.

Important implementation details:
- `GREconv` stores raw/cooked mode plus retunnel addresses: home address, north, south, care-of address, sequence, suspend flags, and uplink key.
- Fixed-size rings buffer pending/downlink/uplink packets during retunnel suspension.
- `gredownlink()` rewrites GRE headers for downlink forwarding, ensures a sequence number, and keeps metadata at the block base.
- `greuplink()` rewrites uplink source/destination and optionally inserts a GRE key.
- `greiput()` first checks retunnel matches on inner IPv4 source/destination, then falls back to raw or address/protocol conversation matching.
- Conversations are limited to 64.

Dependencies and integration:
- Uses `Fsstdconnect()` and `Fsconnected()` from `devip.c`.
- Sends packets through `ipoput4()`.
- Uses `Route`/forwarding integration indirectly through normal IP receive.
- Uses `qbypass()` for direct write-side packet processing.

Research notes:
- This is IPv4-only GRE; headers and address fields are IPv4.
- The retunneling logic is specialized and stateful, with explicit suspend/resume controls.
- Some code comments highlight deliberate packet loss in lock-race situations to avoid blocking receive paths.

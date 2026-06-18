# File Research: sources/os/plan9/plan9/sys/src/9/ip/icmp.c

Implements ICMPv4 as a devip protocol.

Key responsibilities:
- Registers protocol `icmp` for IP protocol number 1.
- Creates read queues and bypass write handling.
- Uses standard connect/announce helpers for addressing and conversation setup.
- `icmpkick` fills IPv4 and ICMP fields, sets local/remote addresses, writes ICMP id from local port, computes checksum, updates stats, and sends via `ipoput4`.
- Emits ICMP TTL exceeded, destination/port unreachable, and fragmentation-needed messages for IPv4 stack error paths.
- `icmpiput` validates length and checksum, counts message types, replies to echo requests, maps unreachable/time-exceeded payloads to protocol `advise` callbacks when possible, and otherwise delivers matching ICMP packets to conversations.
- `icmpadvise` hangs up matching ICMP conversations on lower-layer advice.
- `icmpstats` reports aggregate and per-type in/out counters.

Notable design:
- Conversation matching for received ICMP uses ICMP id plus remote address.
- Error advice unwraps the embedded original IP header to find the affected protocol.

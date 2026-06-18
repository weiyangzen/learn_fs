# File Research: sources/os/plan9/9front/sys/src/cmd/ip/tinc.c

This is a Plan 9 implementation of a tinc-like VPN node. It manages host/subnet topology, authenticated meta connections, encrypted packet transport, and routing through a Plan 9 packet `ipifc`.

Key behavior:
- Reads host config files with RSA public keys, Address, Port, Subnet, PMTU, TCP-only, indirect-data, MSS clamp, and PMTU discovery settings.
- Authenticates meta TCP connections using RSA via factotum and negotiates AES keys.
- Propagates graph updates: subnets, edges, key changes, key requests/answers, ping/pong, and TCP packet fallback.
- Encrypts UDP packet traffic with AES-CBC plus truncated SHA2-256 HMAC and replay tracking.
- Routes Ethernet-framed IPv4/IPv6 packets, supports VLAN stripping, subnet lookup, TCP MSS clamping, UDP fast path, and TCP fallback.
- Creates a Plan 9 `ipifc` packet interface and runs rc hook scripts for host/subnet/up/down events.

Research notes:
- Uses global graph arrays protected by `netlk`, with `lconn` preventing echoing updates back to the origin.
- Default PMTU accounts for worst-case UDPv6 over 6in4 over PPPoE plus crypto overhead.

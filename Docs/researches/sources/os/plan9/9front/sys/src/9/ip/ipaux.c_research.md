# File Research: sources/os/plan9/9front/sys/src/9/ip/ipaux.c

Provides IP stack auxiliary routines and shared constants: IPv6 well-known addresses, protocol checksum calculation, MAC parsing, multicast detection, connection IP-version selection, IP hash-table management, NAT translation management, and checksum-adjusting helpers.

Key responsibilities:
- Defines `v6hdrtypes` names and well-known IPv6 addresses/prefixes.
- Computes protocol checksums across block lists with `ptclcsum()`.
- Builds IPv6 solicited-node multicast addresses with `ipv62smcast()`.
- Parses MAC addresses with `parsemac()`.
- Detects multicast addresses with `ipismulticast()`.
- Chooses conversation IP version with `convipvers()`.
- Implements `Ipht` add/remove/lookup for conversations and translations.
- Implements NAT translation lifecycle and user-visible translation read/write operations.
- Provides `hnputs_csum()` for incremental checksum updates.

Important implementation details:
- `iphtlook()` applies precedence: exact 4-tuple, local address+port, any address+port, local address only, then wildcard.
- NAT `Translation` entries are held on an active LRU-style list and a free list; expired or excessive entries are reused.
- `transforward()` creates source-translation state only after checking source validity, forward route, local egress address, backward route, and port availability.
- UDP and ICMP backward translations may match replies from any remote endpoint to support hole punching.
- `transwrite()` can flush all translations with zero-length write at offset 0, or install a specific translation after validating routes and local addresses.
- `ptclcsum()` handles chained `Block` lists and odd byte alignment by accumulating low/high sums separately.

Dependencies and integration:
- Used by ICMP, UDP/TCP-like protocols, route translation, GRE/ESP checksums, and IPv6 neighbor code.
- Depends on `ipv6.h` constants and route/interface functions from the broader IP stack.

Research notes:
- Despite the filename, this is not just parsing glue; it contains central NAT and protocol lookup mechanics.
- Translation-related typo strings exist in error messages (`desination`, `soruce`) but do not affect behavior.

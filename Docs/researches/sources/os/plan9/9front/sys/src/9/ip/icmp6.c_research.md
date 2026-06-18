# File Research: sources/os/plan9/9front/sys/src/9/ip/icmp6.c

Implements ICMPv6, including user conversations, echo handling, error generation/advice, neighbor discovery, and validation rules for NDP/router messages.

Key responsibilities:
- Registers protocol `icmpv6` for `ICMPv6`.
- Sends user ICMPv6 packets through `icmpkick6()`.
- Receives ICMPv6 packets through `icmpiput6()`.
- Generates IPv6 errors: no host, no conversation, TTL exceeded, packet too big.
- Sends neighbor solicitations via `icmpns6()` and neighbor advertisements via `icmpna6()`.
- Validates ICMPv6 and NDP packets in `valid()`.
- Supports a `headers` control mode where user payload includes source/destination address fields.

Important implementation details:
- ICMPv6 checksum is calculated by temporarily reusing the IPv6 header area as a pseudoheader.
- NDP validation enforces hop limit 255, code 0, target/multicast constraints, option length constraints, and router-advertisement source checks.
- Neighbor solicitation for a local/proxy target may insert sender link-layer info into ARP/NDP cache and reply with appropriate R/S/O flags.
- Neighbor advertisement updates the ARP/NDP cache, including tentative-address handling for duplicate address detection.
- Embedded first-fragment headers are normalized before advice dispatch when possible.

Dependencies and integration:
- Reuses ICMPv4 connection/open/close/state helpers where possible.
- Calls `arpenter`, `arpforme`, `ipv6local`, `iplocalonifc`, `Fsrcvpcolx`, and `ipoput6`.
- Used by `ethermedium.c` for NDP and DAD flows.

Research notes:
- This file is central to IPv6 control-plane correctness.
- The implementation assumes no extension headers for checksum validation except where advice strips a first fragment header.
- It records detailed error counters for hop-limit, code, target, option length, address mix, and router-address failures.

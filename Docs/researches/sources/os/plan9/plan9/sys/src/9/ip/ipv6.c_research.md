# File Research: sources/os/plan9/plan9/sys/src/9/ip/ipv6.c

Implements core IPv6 output, input, extension-header handling, and fragment reassembly.

Key responsibilities:
- `ipoput6` performs IPv6 output: tentative-source rejection, length validation, route lookup, gateway/interface selection, traffic class/hop limit setup, MTU checks, packet-too-big generation, source fragmentation, and medium write.
- Honors IPv6 rule that intermediate nodes do not fragment gated packets unless the outgoing interface is marked for reassembly/NAT-style handling.
- `ipiput6` performs IPv6 input: header pullup, self-address/tentative checks, version validation, forwarding policy, link-local forwarding rejection, hop-limit handling, extension processing, optional reassembly, and protocol dispatch.
- `procxtns` and `unfraglen` identify hop-by-hop/routing/fragment headers and optionally rewrite the next-header slot to insert a fragment header.
- `procopts` is currently a pass-through.
- `ip6reassemble` mirrors IPv4 reassembly for IPv6 fragments, keyed by source/destination/id, trims overlaps, removes fragment headers on completion, and updates payload length.
- `ipfragallo6` and `ipfragfree6` manage IPv6 fragment queue objects.

Notable behavior:
- Fragment offset accounting uses the IPv6 unfragmentable-part length rather than a fixed IP header length.
- ICMPv6 packet-too-big and time-exceeded generation is integrated into forwarding/output error paths.

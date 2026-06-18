# sources/user-network-fs/impacket/impacket/NDP.py

## Purpose

`NDP.py` provides small builders for IPv6 Neighbor Discovery Protocol ICMPv6 messages and options. It wraps `ICMP6` from Impacket and constructs router solicitation, router advertisement, neighbor solicitation, neighbor advertisement, redirect, and standard NDP option payloads.

## Important APIs, Types, and Functions

`NDP` subclasses `ICMP6` and defines type constants `ROUTER_SOLICITATION`, `ROUTER_ADVERTISEMENT`, `NEIGHBOR_SOLICITATION`, `NEIGHBOR_ADVERTISEMENT`, and `REDIRECT`. Class methods build initialized messages: `Router_Solicitation`, `Router_Advertisement`, `Neighbor_Solicitation`, `Neighbor_Advertisement`, and `Redirect`. `append_ndp_option` appends option bytes to the message payload child.

`NDP_Option` is a factory-style class with constants for source link-layer address, target link-layer address, prefix information, redirected header, and MTU. Its class methods return `ImpactPacket.Data` objects containing encoded option bytes.

## Control Flow

Each NDP message builder packs fixed fields with `struct.pack`, appends IPv6 address bytes where needed, and delegates to private `__build_message`. That helper creates an `NDP`, sets ICMPv6 type and code zero, wraps the message-specific body in `ImpactPacket.Data`, and attaches it as the child payload. Option builders compute the NDP option length in 8-octet units, prepend type and length, and return a data payload that `append_ndp_option` can append to the existing child buffer.

## State and Persistence Behavior

There is no durable state. Message instances store mutable ICMPv6 header bytes and a child `Data` payload inherited from `ImpactPacket` composition. `append_ndp_option` mutates the child payload in place and assumes a child already exists. Option factories return independent `Data` buffers.

## Dependencies and Integration Points

The file depends on `array`, `struct`, `impacket.ImpactPacket`, and `impacket.ICMP6.ICMP6`. It expects target and destination IPv6 address objects to provide `as_bytes()`, matching Impacket's IPv6 address helpers. It integrates with IPv6 packet building by acting as an ICMPv6 header child inside the normal Impacket packet graph.

## Risks and Edge Cases

Several length calculations use `/`, which yields a float under Python 3. Those values are later packed as bytes and can fail unless integer conversion happens elsewhere. Link-layer address comments require multiples of 8 octets but the code does not validate this. `append_ndp_option` will fail if the message has no child payload. The builders do not compute ICMPv6 checksums themselves; checksum correctness depends on the inherited ICMP6/IP6 stack.

## Test Signals

Tests should serialize each NDP message type and compare fixed fields, flags, address bytes, and option lengths against RFC 4861 examples. Negative tests should cover non-multiple-of-8 link-layer addresses, appending an option to a bare `NDP`, and Python 3 option length type behavior.

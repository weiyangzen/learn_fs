# sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6_Extension_Headers.py

## Purpose

`test_IP6_Extension_Headers.py` validates construction, chaining, containment, and decoding of IPv6 hop-by-hop, destination options, routing options, and padding option headers.

## Important APIs, Types, And Functions

The file imports `unittest`, `six.PY2`, `IP6`, `ImpactDecoder`, and `IP6_Extension_Headers`. `TestIP6.string_to_list()` normalizes byte iteration. Test methods cover simple header creation, IPv6 containment, option addition and padding, chained extension headers, direct decoders, full IPv6-chain decoding, and bytes-string decoding.

## Control Flow

Construction tests instantiate `Hop_By_Hop`, `Destination_Options`, and `Routing_Options`, set next headers and routing fields, add `Option_PAD1`/`Option_PADN`, and compare bytes plus sizes. Chaining tests use `.contains()` to nest extension headers and attach them to IPv6. Decoder tests feed byte fixtures to specific decoders and assert next headers, extension lengths, routing fields, header type, and option metadata.

## State And Persistence Behavior

All state is local packet fixtures and constructed packet objects. There is no network or disk behavior.

## Dependencies And Integration Points

It exercises `impacket.IP6_Extension_Headers`, `IP6.IP6.contains()`, extension header size calculation, option padding, child chaining, and `ImpactDecoder` dispatch.

## Risks And Edge Cases

The byte-exact fixtures are sensitive to intentional serialization changes. Malformed lengths, unknown option actions, jumbo options, fragmentation, authentication, and ESP headers are not covered.

## Test Signals

Passing tests signal stable extension header serialization, padding, next-header propagation, chaining, and decoder dispatch for the covered basic headers.

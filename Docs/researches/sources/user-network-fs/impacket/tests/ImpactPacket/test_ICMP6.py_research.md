# sources/user-network-fs/impacket/tests/ImpactPacket/test_ICMP6.py

## Purpose

`test_ICMP6.py` validates ICMPv6 construction and decoding. It checks byte-exact generated ICMPv6 packets after IPv6 pseudo-header checksum calculation and verifies decoder accessors for echo and error-message fields.

## Important APIs, Types, And Functions

The test imports `unittest`, `IP6`, `ImpactDecoder`, and `ICMP6`. `TestICMP6.setUp()` builds packet lists, message descriptions, and reference bytes. Helpers are `encapsulate_icmp6_packet_in_ip6_packet()`, `compare_icmp6_packet_with_reference_buffer()`, and `generate_icmp6_constructed_packets()`. Test methods are `test_message_construction()` and `test_message_decoding()`.

## Control Flow

Setup constructs echo request/reply, parameter problem variants, destination unreachable variants, time exceeded variants, and packet-too-big messages. Construction embeds each ICMPv6 packet in a fixed IPv6 packet, sets next header and payload length, calculates the checksum, and compares serialized bytes. Decoding feeds references to `ICMP6Decoder` and asserts type, code, echo ID/sequence/data, parameter pointer, originating packet data, and MTU.

## State And Persistence Behavior

State is per-test in-memory fixtures only. There is no network or disk behavior.

## Dependencies And Integration Points

The file exercises `impacket.ICMP6`, `impacket.IP6`, and `ImpactDecoder.ICMP6Decoder`, including parent/child checksum integration.

## Risks And Edge Cases

Coverage is limited to selected ICMPv6 echo and error messages. It does not cover neighbor discovery, router discovery, malformed lengths, unknown codes, or checksum failure behavior.

## Test Signals

Passing tests signal stable ICMPv6 constructors, pseudo-header checksum calculation, decoder dispatch, and accessors for the covered messages.

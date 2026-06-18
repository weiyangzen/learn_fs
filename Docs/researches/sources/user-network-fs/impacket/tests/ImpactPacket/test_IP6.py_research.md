# sources/user-network-fs/impacket/tests/ImpactPacket/test_IP6.py

## Purpose

`test_IP6.py` validates IPv6 header decoding and construction for a fixed UDP-carrying IPv6 header.

## Important APIs, Types, And Functions

It imports `unittest`, `IP6`, and `ImpactDecoder`. `TestIP6.setUp()` defines a 40-byte reference header. `test_decoding()` verifies field extraction via `IP6Decoder`; `test_creation()` builds a packet with setters and compares serialized bytes.

## Control Flow

Decoding checks version, traffic class, flow label, payload length, next header, hop limit, and compressed source/destination addresses. Creation sets the same values on a new `IP6.IP6()` and compares `get_bytes().tolist()` to the fixture.

## State And Persistence Behavior

State is an in-memory reference header. There is no persistence.

## Dependencies And Integration Points

The test exercises IPv6 bitfield packing/unpacking, `IP6_Address` formatting through accessors, and `ImpactDecoder.IP6Decoder`.

## Risks And Edge Cases

It covers one unfragmented IPv6 header only. Extension headers, invalid versions, jumbo payloads, boundary values, and payload mismatches are outside this file.

## Test Signals

Passing tests indicate stable IPv6 header serialization and decoding for the selected fixture.

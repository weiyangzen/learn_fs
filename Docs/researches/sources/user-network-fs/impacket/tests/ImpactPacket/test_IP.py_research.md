# sources/user-network-fs/impacket/tests/ImpactPacket/test_IP.py

## Purpose

`test_IP.py` is a narrow regression test for IPv4 fragmentation when an `IP` packet has no payload.

## Important APIs, Types, And Functions

It imports `unittest` and `impacket.ImpactPacket.IP`. The only test class is `TestIP`; the only test method is `test_fragment_by_size_without_payload()`.

## Control Flow

The test creates an empty `IP()` packet, calls `fragment_by_size(8)`, and asserts the returned list is exactly `[ip]`.

## State And Persistence Behavior

State is local to the test. There is no persistence or network I/O.

## Dependencies And Integration Points

It exercises `ImpactPacket.IP.fragment_by_size()` for payload-less packets.

## Risks And Edge Cases

It does not cover payload fragmentation, offsets, flags, checksums, invalid sizes, or child protocol propagation. It only guards the no-payload edge case.

## Test Signals

Passing this test signals that empty IPv4 packets do not crash or mutate unexpectedly when fragmented by size.

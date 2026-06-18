# sources/user-network-fs/impacket/tests/ImpactPacket/test_LinuxSLL.py

## Purpose

`test_LinuxSLL.py` validates selected setters/getters and serialization for Linux cooked capture (`LinuxSLL`) packets.

## Important APIs, Types, And Functions

It imports `unittest` and `LinuxSLL`. `TestLinuxSLL` defines `test_set_arphdr()` and `test_set_addr_bytes()`.

## Control Flow

One test sets ARP hardware type `513` and reads it back. The other sets a six-byte address, asserts it is padded to eight bytes, and asserts serialized packet length is 16 bytes.

## State And Persistence Behavior

State is local to each packet object. There is no persistence.

## Dependencies And Integration Points

It exercises `ImpactPacket.LinuxSLL` field setters/getters, address padding, and header serialization length.

## Risks And Edge Cases

It does not test packet type, address length, protocol field, existing-frame decoding, overlong addresses, or invalid ranges.

## Test Signals

Passing tests signal stable ARP hardware field handling and short-address padding.

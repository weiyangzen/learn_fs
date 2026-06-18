# sources/user-network-fs/impacket/tests/ImpactPacket/test_IP_fragment_issue2095.py

## Purpose

`test_IP_fragment_issue2095.py` is a regression test for issue 2095: IPv4 fragmentation must not crash when the payload is a generic `Data` object with no protocol number.

## Important APIs, Types, And Functions

It imports `unittest`, `IP`, and `Data`. `TestIPFragmentIssue2095.test_fragment_by_list_with_data_payload()` is the only test.

## Control Flow

The test creates an `IP()` packet, attaches `Data(b'HELLO WORLD')`, calls `fragment_by_list([8])`, and asserts the result is a non-empty list.

## State And Persistence Behavior

State is local packet and fragment objects. There is no persistence.

## Dependencies And Integration Points

It exercises `IP.contains()`, generic `Data`, and `IP.fragment_by_list()` handling of children whose protocol is `None`.

## Risks And Edge Cases

The test does not verify exact fragment offsets, flags, checksums, or payload bytes. It only guards the crash condition.

## Test Signals

Passing this test signals that the issue 2095 crash path remains fixed for generic data payload fragmentation.

# sources/user-network-fs/impacket/tests/dot11/test_FrameControlPSPoll.py

## Purpose
This unit test validates Power Save Poll control-frame parsing and mutation.

## Important APIs, Types, and Functions
It uses `Dot11`, `Dot11Types`, and `Dot11ControlFramePSPoll`. Covered fields are AID, BSSID, transmitter address, header size, and tail size via `get_aid/set_aid`, `get_bssid/set_bssid`, and `get_ta/set_ta`.

## Control Flow
`setUp()` parses a static PS-Poll frame, confirms control type and PS-Poll subtype constants, constructs the specialized body parser, and attaches it to the parent. Tests check body dimensions, mutate AID, mutate BSSID endpoints, and mutate TA endpoints.

## State and Persistence Behavior
State is local to packet buffers. The test verifies that setter methods update the mutable in-memory representation.

## Dependencies and Integration Points
This integrates the generic dot11 parser with the PS-Poll body layout, which differs from other control frames by using AID instead of a standard duration field.

## Risks
The test covers field access but not serialized full-frame output after mutation. It does not cover boundary behavior for AID reserved bits.

## Test Signals
Signals include subtype recognition, 14-byte body size, initial AID `0xAFF1`, BSSID and TA extraction, and setter/getter round trips.

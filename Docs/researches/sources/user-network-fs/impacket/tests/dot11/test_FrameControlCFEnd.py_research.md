# sources/user-network-fs/impacket/tests/dot11/test_FrameControlCFEnd.py

## Purpose
This unit test validates 802.11 CF-End control-frame body parsing and field mutation.

## Important APIs, Types, and Functions
It uses `Dot11`, `Dot11Types`, and `Dot11ControlFrameCFEnd`. Covered accessors are header/tail size, `get_duration/set_duration`, `get_ra/set_ra`, and `get_bssid/set_bssid`.

## Control Flow
`setUp()` parses a fixed CF-End frame, asserts control type/subtype/type-subtype constants, creates `Dot11ControlFrameCFEnd` from the top-level body, and attaches it as a child. Tests validate the 14-byte control body and mutate duration, receiver address, and BSSID.

## State and Persistence Behavior
Only in-memory packet field state changes. No external state or persistence.

## Dependencies and Integration Points
The file tests the integration between generic frame-control decoding and a specialized control-frame body class with two MAC-address fields.

## Risks
Coverage is field-level and does not assert complete serialized packet bytes after mutation. It assumes byte arrays are mutable and expose `tolist()`.

## Test Signals
Signals include exact subtype recognition, expected broadcast RA and BSSID bytes from the sample, duration endian correctness, and setter/getter round trips for both address fields.

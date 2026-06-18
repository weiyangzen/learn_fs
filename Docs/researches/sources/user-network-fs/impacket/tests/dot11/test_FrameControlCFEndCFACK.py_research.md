# sources/user-network-fs/impacket/tests/dot11/test_FrameControlCFEndCFACK.py

## Purpose
This file validates parsing and mutation for combined CF-End + CF-ACK 802.11 control frames.

## Important APIs, Types, and Functions
It uses `Dot11`, `Dot11Types`, and `Dot11ControlFrameCFEndCFACK`. Accessors under test are body size, tail size, duration, receiver address, and BSSID getters/setters.

## Control Flow
`setUp()` parses a static frame, verifies the control subtype and combined type/subtype constant, creates the specialized body parser from the generic body string, and links it as a child. Tests assert initial field values, mutate selected bytes or duration, and re-read through getters.

## State and Persistence Behavior
State is confined to the in-memory packet object and its mutable address buffers.

## Dependencies and Integration Points
The test checks that the generic dot11 frame layer and the CF-End-CF-ACK body class agree on body boundaries and subtype semantics.

## Risks
No final packet-level serialization is asserted after mutation. The static sample is the only fixture, so malformed or truncated variants are not covered.

## Test Signals
Signals include exact duration `0xEDDE`, body size of 14 bytes, correct RA/BSSID extraction, and address mutation persistence through setters.

# sources/user-network-fs/impacket/tests/dot11/test_FrameControlRTS.py

## Purpose
This file validates Request-To-Send control-frame parsing and mutation.

## Important APIs, Types, and Functions
It uses `Dot11`, `Dot11Types`, and `Dot11ControlFrameRTS`. Covered body APIs are size getters, `get_duration/set_duration`, `get_ra/set_ra`, and `get_ta/set_ta`.

## Control Flow
`setUp()` parses a static RTS frame, asserts control type and RTS subtype constants, creates the specialized RTS body object from the parent body, and links it as a child. Tests verify body size, duration, receiver address, and transmitter address mutations.

## State and Persistence Behavior
No external state exists. Mutations are packet-buffer updates inside the test instance.

## Dependencies and Integration Points
The test checks agreement between top-level `Dot11` frame-control parsing and the RTS body layout containing both RA and TA fields.

## Risks
No full serialized packet assertion follows setter calls, and only one sample frame is covered.

## Test Signals
Signals include exact RTS subtype recognition, 14-byte body size, initial duration `0x181`, and address setter round trips for RA and TA.

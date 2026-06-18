# sources/user-network-fs/impacket/tests/dot11/test_FrameControlCTS.py

## Purpose
This unit test validates Clear-To-Send control-frame parsing for 802.11.

## Important APIs, Types, and Functions
It uses `Dot11`, `Dot11Types`, and `Dot11ControlFrameCTS`, covering `get_header_size`, `get_tail_size`, `get_duration/set_duration`, and `get_ra/set_ra`.

## Control Flow
`setUp()` decodes a static CTS frame, asserts control and CTS subtype constants, constructs the CTS body from the parent body bytes, and attaches it with `contains()`. Tests verify the body size and mutate duration and receiver address.

## State and Persistence Behavior
All state is local in packet buffers. Mutations verify field-level updates only.

## Dependencies and Integration Points
The file verifies the specialized CTS body parser's alignment with the generic `Dot11` body boundary and type/subtype logic.

## Risks
It does not validate full packet bytes after setter calls, and only one fixture is used. Address mutation assumes a mutable array-like return value.

## Test Signals
Signals include CTS subtype recognition, 8-byte control body size, expected initial duration 4667, and RA round-trip mutation.

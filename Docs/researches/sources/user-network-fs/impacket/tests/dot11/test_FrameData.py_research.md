# sources/user-network-fs/impacket/tests/dot11/test_FrameData.py

## Purpose
This file validates parsing and mutation of a standard 802.11 data frame body.

## Important APIs, Types, and Functions
`TestDot11DataFrames` uses `Dot11`, `Dot11Types`, and `Dot11DataFrame`. It covers header/tail size, duration, address1/address2/address3 getters and setters, sequence-control accessors, fragment-number masking, sequence-number masking, and `get_frame_body`.

## Control Flow
`setUp()` parses a fixed data frame, asserts data type/subtype constants, builds `Dot11DataFrame` from the parent body bytes, and attaches it. Tests mutate duration and address fields, set sequence-control fields, verify bit masking for 4-bit fragment and 12-bit sequence numbers, and compare payload bytes for a frame without address4.

## State and Persistence Behavior
State is local in packet objects. The important behavior is mutation of packed sequence-control subfields without corrupting unrelated bits.

## Dependencies and Integration Points
The test integrates top-level dot11 frame-control parsing with the data-frame body parser and payload extraction used before LLC/IP decoding.

## Risks
It covers a no-address4 data frame only, leaving ToDS/FromDS combinations with a fourth address untested. It does not assert full-packet serialization after each setter.

## Test Signals
Signals include type/subtype recognition, exact header size of 22 bytes, duration and MAC address round trips, fragment/sequence bit masking, and exact frame-body payload comparison.

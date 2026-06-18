# sources/user-network-fs/impacket/tests/dot11/test_FrameControlACK.py

## Purpose
This unit test validates parsing and mutation of 802.11 ACK control-frame bodies.

## Important APIs, Types, and Functions
`TestDot11FrameControlACK` uses `Dot11` to parse frame control, `Dot11Types` constants to assert type/subtype identity, and `Dot11ControlFrameACK` for body-level accessors. It exercises `get_header_size`, `get_tail_size`, `get_duration/set_duration`, and `get_ra/set_ra`.

## Control Flow
`setUp()` parses a static ACK frame, asserts it is a control acknowledgment, constructs the ACK body object from `d.get_body_as_string()`, and attaches it with `d.contains(self.ack)`. Tests then validate size and mutate duration and receiver address.

## State and Persistence Behavior
State is local packet-buffer mutation only. Address setters update an array-like field copied back into the frame body.

## Dependencies and Integration Points
The file integrates top-level `Dot11` frame-control parsing with the specialized ACK control-frame class.

## Risks
The test does not assert final full-frame serialization after mutations, only accessor round trips. It also assumes `get_ra()` returns an object supporting `tolist()` and item assignment.

## Test Signals
Signals include correct ACK subtype dispatch, ACK body size of 8 bytes with no tail, little-endian duration handling, and receiver-address round-trip mutation.

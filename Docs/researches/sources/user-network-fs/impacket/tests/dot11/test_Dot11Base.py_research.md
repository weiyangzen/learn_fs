# sources/user-network-fs/impacket/tests/dot11/test_Dot11Base.py

## Purpose
This unit test validates core `Dot11` frame-control parsing and mutation. It checks header/tail sizing, version/type/subtype extraction, individual bit flags, combined type/subtype setting, and final serialized bytes for a crafted control frame.

## Important APIs, Types, and Functions
`TestDot11Common` constructs `Dot11` from a fixed byte string. It exercises `get_header_size`, `get_tail_size`, `get_version/set_version`, `get_type/set_type`, `get_subtype/set_subtype`, flag getters/setters (`toDS`, `fromDS`, `moreFrag`, `retry`, `powerManagement`, `moreData`, `order`), `set_type_n_subtype`, and `get_packet`. `Dot11Types` supplies named constants.

## Control Flow
`setUp()` creates a fresh `Dot11` instance for each test, so mutations are isolated. Each test reads the initial parsed value, writes a replacement, and asserts the updated value. The final test sets a power-save poll type/subtype and multiple flags, then compares the complete packet bytes.

## State and Persistence Behavior
State is in-memory only inside the `Dot11` object. Mutator tests verify that bit-level changes update the serialized packet. No files, network, or shared state are touched.

## Dependencies and Integration Points
The file depends on `unittest`, `impacket.dot11.Dot11`, and `Dot11Types`. It is a local unit test and does not require the remote DCE/RPC infrastructure.

## Risks
The disabled WEP bit test leaves one frame-control bit without active coverage. Tests assert exact byte order and bit layout, so they are sensitive to intentional representation changes but useful for regression detection.

## Test Signals
Signals are direct equality assertions for bitfield getters/setters and a complete packet byte comparison, providing strong regression coverage for frame-control packing.

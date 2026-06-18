# sources/user-network-fs/impacket/tests/dot11/test_Dot11Decoder.py

## Purpose
This unit test validates the 802.11 decoder chain in `impacket.ImpactDecoder.Dot11Decoder`. It decodes a captured WEP-protected data frame and verifies the resulting protocol hierarchy.

## Important APIs, Types, and Functions
`TestDot11Decoder` uses `Dot11Decoder().decode()`, then walks `child()` links through `Dot11`, `Dot11DataFrame`, `Dot11WEP`, and encrypted payload/data nodes. It uses `six.PY2` to account for Python 2 class string formatting. Optional WEP-key paths reference LLC and WEP data verification but are inactive because `self.WEPKey` is `None`.

## Control Flow
`setUp()` decodes a static `WEPData` byte string once per test and records successive child nodes. Tests compare class string representations for the top decoder layers. If a WEP key were supplied, additional child nodes would be initialized and validated; otherwise tests return early or assert that the undecoded payload is `ImpactPacket.Data`.

## State and Persistence Behavior
All state is local to decoded packet objects. No persistence or external I/O occurs.

## Dependencies and Integration Points
The file integrates `ImpactDecoder` with `impacket.dot11` packet classes and `ImpactPacket.Data`. It is a unit-level signal that decoder dispatch connects frame-control parsing to protocol object construction.

## Risks
Most encrypted-payload coverage is inactive because there is no WEP key, so LLC decoding and decrypted payload assertions are not normally exercised. Class checks rely on string formatting, which is less robust than `isinstance` and keeps compatibility branches for Python 2.

## Test Signals
Signals include hierarchy construction from raw bytes, correct dispatch to `Dot11DataFrame` and `Dot11WEP`, and fallback to opaque `ImpactPacket.Data` when encrypted data is not decrypted.

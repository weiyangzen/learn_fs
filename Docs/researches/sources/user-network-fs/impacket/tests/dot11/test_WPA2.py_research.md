# sources/user-network-fs/impacket/tests/dot11/test_WPA2.py

Purpose: Tests structural parsing of WPA2/CCMP Dot11 data frames.

Important APIs, types, and functions: Uses `Dot11`, `Dot11DataFrame`, `Dot11WPA2`, `Dot11WPA2Data`; exercises `is_WPA2`, `get/set_extIV`, `get/set_keyid`, `get/set_PN0` through `get/set_PN5`, `WPA2Data.body_string`, `get_MIC`, and `set_MIC`.

Control flow: Setup parses a raw Dot11 data frame into WPA2 header/data objects. Tests mutate protected header fields, assert encrypted body slicing, and validate MIC replacement.

State and persistence behavior: In-memory packet parsing and mutation only. No crypto keys or decrypted payload state.

Dependencies and integration points: Tests the Dot11 protected-data subtype path and WPA2 packet classes, but not CCMP decryption.

Risks: Packet-number field offsets and bit masking are error-prone. Absence of decrypt tests means payload confidentiality/integrity logic is not covered here.

Test signals: Good structural signal for WPA2 recognition, PN field setters/getters, encrypted body boundaries, and MIC accessors.

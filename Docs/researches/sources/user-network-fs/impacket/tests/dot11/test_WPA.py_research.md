# sources/user-network-fs/impacket/tests/dot11/test_WPA.py

Purpose: Tests parsing of a WPA/TKIP-style Dot11 data frame header and encrypted payload metadata.

Important APIs, types, and functions: Uses `Dot11`, `Dot11DataFrame`, `Dot11WPA`, and `Dot11WPAData`; exercises `is_WPA`, `get/set_extIV`, `get/set_keyid`, `get/set_WEPSeed`, `get/set_TSC0` through `get/set_TSC5`, `get_MIC`, `set_MIC`, and `get_icv`.

Control flow: Setup parses a raw data frame into Dot11 data, WPA header, and WPA data body. Tests mutate header counter fields and validate body, MIC, and ICV extraction.

State and persistence behavior: Mutates packet bytes in memory only; no decryption state or key material is used.

Dependencies and integration points: Covers WPA header/body classes inside the Dot11 parser without invoking crypto.

Risks: Decryption is explicitly TODO, so this catches structural parsing but not TKIP correctness. Bitfield setters for extIV/key ID/TSC fields are the main risk.

Test signals: Provides regression vectors for WPA classification, counter field accessors, body slicing, MIC replacement, and ICV offset handling.

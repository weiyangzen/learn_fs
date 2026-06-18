# sources/user-network-fs/impacket/tests/dot11/test_WEPDecoder.py

Purpose: Tests decoding and decryption of an encrypted 802.11 WEP data frame into LLC/SNAP/IP/ICMP payloads.

Important APIs, types, and functions: Uses `Dot11`, `Dot11DataFrame`, `Dot11WEP`, `Dot11WEPData`, `KeyManager`, `Dot11Decoder`, `IP`, and `ICMP`. Exercises `is_WEP`, IV/key ID accessors, ICV accessors, `get_computed_icv`, `check_icv`, and protocol lookup.

Control flow: Setup manually parses Dot11 and WEP header/body objects and configures a `KeyManager`. Decoder tests then run `Dot11Decoder` with `FCS_at_end(False)` and the key manager to decrypt and walk the resulting protocol stack.

State and persistence behavior: Holds cryptographic key material and decrypted packet bytes in memory only.

Dependencies and integration points: Integrates WEP decryption with Dot11 decoder dispatch, key lookup by MAC address, and downstream IP/ICMP parsing.

Risks: Test vectors depend on exact RC4/WEP semantics and ICV endian handling. A likely typo calls `set_iv` inside the key ID test, so key ID setter coverage is incomplete.

Test signals: Strong signal for WEP frame recognition, decryption, ICV validation, decrypted payload bytes, and nested IP/ICMP extraction.

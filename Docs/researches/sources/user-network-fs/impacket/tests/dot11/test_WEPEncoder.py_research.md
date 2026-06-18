# sources/user-network-fs/impacket/tests/dot11/test_WEPEncoder.py

Purpose: Validates construction and encryption of a WEP-protected Dot11 data frame from scratch.

Important APIs, types, and functions: Builds `Dot11`, `Dot11DataFrame`, `Dot11WEP`, `Dot11WEPData`, `LLC`, `SNAP`, `ImpactPacket.IP`, `ImpactPacket.ICMP`, `ImpactPacket.Data`, and `KeyManager`; exercises `get_icv`, `get_computed_icv`, `set_icv`, `get_encrypted_data`, and `encrypt_frame`.

Control flow: `setUp` constructs the full protocol stack with explicit frame-control flags, addresses, sequence numbers, WEP IV/key ID, LLC/SNAP, IP, ICMP, and payload data. Tests compare computed ICV and encrypted output against known bytes.

State and persistence behavior: All packet and key state is in memory. Encryption mutates the WEP frame payload.

Dependencies and integration points: Connects packet construction APIs to WEP encryption and lower-level IP/ICMP serialization.

Risks: Exact ciphertext is sensitive to IV, key bytes, payload serialization, and CRC/ICV byte order. The key manager is initialized but not directly used in assertions.

Test signals: Strong deterministic vector for WEP ICV computation and encrypted payload output.

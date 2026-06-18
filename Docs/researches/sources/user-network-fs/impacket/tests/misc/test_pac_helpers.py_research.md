# sources/user-network-fs/impacket/tests/misc/test_pac_helpers.py

Purpose: Tests Kerberos PAC helper functions for explicit buffer ordering and AES checksum type inference.

Important APIs, types, and functions: Uses `pac.build_pac_type`, `pac.sign_pac`, `PAC_INFO_BUFFER`, `PAC_SIGNATURE_DATA`, PAC type constants, and Kerberos checksum constants.

Control flow: The first test builds PAC buffers from a dictionary with an explicit order and parses the serialized buffer list to assert order. The second builds placeholder server/private checksums, signs with an AES128 key, and validates checksum type updates and signature lengths.

State and persistence behavior: In-memory PAC byte structures only.

Dependencies and integration points: PAC construction/signing is used by Kerberos ticket tooling, especially forged ticket generation.

Risks: Buffer ordering affects PAC consumer interoperability. Checksum type inference from key length can silently choose the wrong checksum if key encoding assumptions change.

Test signals: Covers ordered PAC serialization, in-place PAC checksum data updates, AES128 checksum inference, and expected four-buffer PAC output.

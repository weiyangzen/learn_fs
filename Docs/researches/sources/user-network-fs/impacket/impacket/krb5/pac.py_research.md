# sources/user-network-fs/impacket/impacket/krb5/pac.py

Purpose: models Microsoft PAC buffers and provides PAC construction/signing helpers for MS-PAC structures embedded in Kerberos authorization data.

Important APIs/types: constants identify PAC buffer types. NDR structures cover validation info, SID/group membership, credentials, supplemental NTLM credentials, delegation info, UPN/DNS info, claims/device info, attributes, and requestor SID. `PACTYPE`, `PAC_INFO_BUFFER`, `PAC_CREDENTIAL_INFO`, `PAC_CLIENT_INFO`, `PAC_SIGNATURE_DATA`, and related `Structure` classes model binary PAC buffers. Helper functions include `get_pad_length()`, `get_block_length()`, `_coerce_hex_key()`, `_ordered_buffer_types()`, `build_pac_type()`, `_normalize_pac_checksum_type()`, `_get_checksum_context()`, and `sign_pac()`.

Control flow and state: `build_pac_type()` orders buffers, computes the PAC header/table offset, pads each blob to 8-byte boundaries, and returns a `PACTYPE`. `sign_pac()` requires server and privsvr checksum buffers, coerces AES/NT hash material, normalizes checksum types if requested, zeroes signatures, builds the checksum blob, computes server checksum over the whole PAC, computes privsvr checksum over the server checksum, updates both buffers, and rebuilds the PAC. The input `pac_infos` dictionary is mutated.

Dependencies and integration: depends heavily on Impacket DCE/RPC NDR types, Kerberos constants/crypto checksum tables, LDAP SID helpers, and `Structure`. Ticket-forging and PAC-inspection code uses these types to build and sign PAC authorization data.

Risks and test signals: `sign_pac()` mutates caller-provided PAC dictionaries, which can surprise callers reusing buffer data. Checksum inference from signature length only works for AES keys of expected size. Unsupported checksum types raise generic exceptions. Tests should verify 8-byte alignment, buffer ordering, deterministic PAC bytes, AES128/AES256/RC4 signatures, missing key errors, inferred checksum types, and mutation side effects.

# sources/user-network-fs/impacket/tests/misc/test_krb5_gssapi.py

Purpose: Tests Kerberos GSSAPI token framing, implementation selection, MIC padding, RC4 wrap/MIC behavior, LDAP wrap round-trip, and AES rotate helpers.

Important APIs, types, and functions: Uses `GSSAPI`, `GSSAPI_RC4`, `GSSAPI_AES128`, `GSSAPI_AES256`, `MechIndepToken`, `KRB_OID`, `_calculateMICPad`, and Kerberos encryption type constants. `_SessionKey` supplies minimal `.contents`.

Control flow: Tests invalid token tags, short/long DER length encoding, token round-trip, MIC pad calculation, factory dispatch by enctype, direction-sensitive RC4 MICs, no-encryption RC4 wrapping, LDAP wrap/unwrap, and AES rotate/unrotate inverse behavior.

State and persistence behavior: In-memory tokens and synthetic session keys only.

Dependencies and integration points: Covers GSSAPI paths used by SMB/LDAP/Kerberos authentication integrations.

Risks: Token length encoding and direction-specific sequence handling are interoperability-sensitive. Tests use synthetic keys, so external KDC behavior is not covered.

Test signals: Good signal for token framing, supported enctype selection, unsupported enctype rejection, RC4 MIC/wrap behavior, LDAP sealing round-trip, and AES rotation helpers.

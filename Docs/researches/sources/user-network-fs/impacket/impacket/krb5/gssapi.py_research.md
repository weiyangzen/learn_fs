# sources/user-network-fs/impacket/impacket/krb5/gssapi.py

Purpose: implements partial Kerberos GSS-API token wrapping and MIC support for RC4 and AES Kerberos session keys, including LDAP-specific wrap/unwrap formats and mechanism-independent token framing.

Important APIs/types: constants define GSS flags and key usages. `MechIndepToken` encodes/decodes the application 0 token with Kerberos OID and BER-style lengths. `CheckSumField` models the AP-REQ checksum field. `GSSAPI(cipher)` selects `GSSAPI_RC4`, `GSSAPI_AES128`, or `GSSAPI_AES256`. RC4 and AES classes expose `GSS_GetMIC()`, `GSS_Wrap()`, `GSS_Unwrap()`, `GSS_Wrap_LDAP()`, and `GSS_Unwrap_LDAP()`.

Control flow and state: methods are stateless except for random confounder generation. RC4 computes HMAC-MD5 signatures, encrypts sequence numbers, optionally seals with ARC4, and has special auth-data handling for DCE/RPC. AES uses RFC 4121 token fields, checksum profiles, encrypts data plus token trailer, and rotates by RRC/EC for wrap tokens. LDAP paths prepend signatures differently from DCE/RPC paths.

Dependencies and integration: depends on PyCryptodome HMAC/MD5/ARC4, `impacket.structure`, `impacket.krb5.crypto`, and Kerberos constants. `ldap.py` uses `GSS_Wrap_LDAP()` for signed/sealed LDAP. `kerberosv5.py` uses `CheckSumField` and GSS flags in AP authenticators.

Risks and test signals: sequence-number verification is minimal; unwrap often mirrors wrap and does not deeply validate token checksums or directions. AES unwrap assumes token sizing and may produce surprising slicing when EC is zero. RC4 confounders are ASCII letters from `SystemRandom` fallback. Tests should cover MIC padding, mechanism length encoding over 127 bytes, RC4/AES LDAP round-trips, DCE/RPC auth-data paths, sequence numbers, encrypt=False paths, and tampered token rejection expectations.

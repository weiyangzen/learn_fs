# sources/user-network-fs/impacket/impacket/krb5/kerberosv5.py

Purpose: provides high-level Kerberos client helpers: send KDC messages over TCP, obtain TGTs and TGSs, build SPNEGO Kerberos Type 1/Type 3 tokens for DCE/RPC, and render Kerberos errors.

Important APIs/types: `sendReceive()` frames KDC TCP messages with 4-byte length and decodes `KRB_ERROR`. `getKerberosTGT()` builds AS_REQ, handles preauth discovery, selects AES or RC4, encrypts PA-ENC-TIMESTAMP, decrypts AS_REP, and returns `(tgt, cipher, key, sessionKey)`. `getKerberosTGS()` builds AP_REQ inside TGS_REQ, decrypts TGS_REP, follows referrals recursively, and returns a new session key. `getKerberosType1()` obtains/cache-loads TGT/TGS and emits SPNEGO NegTokenInit with AP_REQ. `getKerberosType3()` processes AP_REP and returns a NegTokenResp. `SessionKeyDecryptionError` preserves AS-REP cracking context, and `KerberosError` extends SMB `SessionError`.

Control flow and state: functions are mostly stateless, with randomness for nonces. `getKerberosTGT()` first sends an AS_REQ with PAC request, then either handles no-preauth AS_REP or parses `METHOD_DATA` to derive the client key and send timestamp preauth. It falls back from AES to RC4 when KDC reports unsupported enctypes and password hashes are available or computable. `getKerberosType1()` optionally reads ccache before network acquisition.

Dependencies and integration: integrates `asn1`, `types`, `constants`, `crypto`, `ccache`, `gssapi`, `spnego`, SMB session errors, NT status tables, sockets, and pyasn1. LDAP and SMB/RPC clients rely on these helpers for Kerberos authentication.

Risks and test signals: `sendReceive()` assumes TCP and does not use UDP fallback. Recursive referral handling in `getKerberosTGS()` needs loop protection tests. Cipher selection relies on KDC hints and may fail if `encryptionTypesData` lacks the selected enctype. Nonce validation is TODO. Tests should simulate KDC errors, preauth required/no-preauth flows, AES-to-RC4 fallback, cache TGT/TGS use, AP_REP error tokens, generic NT-error rendering, superseded-user rendering, and referral chains.

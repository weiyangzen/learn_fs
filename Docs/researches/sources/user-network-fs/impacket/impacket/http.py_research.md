# sources/user-network-fs/impacket/impacket/http.py

Purpose: provides `HTTPClientSecurityProvider`, a small HTTP authentication helper for MS-RPCH style clients and relay-friendly flows. It supports Basic and NTLM in practice, advertises constants for Auto, Basic, NTLM, Negotiate, Bearer, and Digest, and exposes a separate NTLM Type 1 send path so callers can inject or relay negotiate messages.

Important APIs: `set_credentials()` stores cleartext credentials, LM/NT hashes, AES keys, and optional Kerberos tickets, though Kerberos is explicitly rejected for HTTP NTLM/Basic paths. `parse_www_authenticate()` extracts offered schemes by substring. `connect()` returns `HTTPConnection` or `HTTPSConnection`. `get_auth_headers()` dispatches to Basic or Auto/NTLM. `send_ntlm_type1()` sends a zero-length authorized request, expects a 401 challenge, captures `WWW-Authenticate`, stores NTLM target info as AV pairs, and returns the raw challenge. `get_auth_headers_auto()` completes NTLM Type 3 or falls back to Basic if Auto discovered Basic.

Control flow and state: the object is stateful. Credentials, selected auth type, discovered auth types, and NTLM target info persist across calls. Auto mode mutates `__auth_type` to `NTLM` or `Basic` after negotiation. The NTLM path performs network I/O during header construction because it must obtain a server challenge.

Dependencies and integration: relies on stdlib `http.client`/`httplib`, `ssl`, `base64`, `re`, `binascii`, and `impacket.ntlm`. It is intended to be plugged into HTTP protocol clients that can pass an open HTTP object plus method/path/header context.

Risks and test signals: `parse_www_authenticate()` is substring-based and case-sensitive, so unusual header casing or scheme names embedded in parameters can mis-detect. Basic refuses hashes/AES/TGT/TGS but sends base64 cleartext when enabled. HTTPS uses `ssl.PROTOCOL_SSLv23`, which is a legacy compatibility choice. Tests should cover odd-length hash normalization, 401 challenge parsing, no-NTLM fallback to Basic, unsupported auth types, absence of `WWW-Authenticate`, and preservation of NTLM AV pair metadata.

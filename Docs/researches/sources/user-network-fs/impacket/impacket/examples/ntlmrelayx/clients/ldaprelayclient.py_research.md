# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/ldaprelayclient.py

## Purpose
`ldaprelayclient.py` implements LDAP and LDAPS relay target clients using ldap3's Sicily NTLM bind path. It supports normal relays and flag-stripping modes used by ntlmrelayx options for MIC/sign/seal removal.

## Important APIs, Types, and Functions
`LDAPRelayClient` exposes `initConnection()`, `sendNegotiate()`, `sendAuth()`, fake ldap3 callbacks `create_negotiate_message()` and `create_authenticate_message()`, `parse_challenge_message()`, and `keepAlive()`. `LDAPSRelayClient` changes the server URI and default port. `MODIFY_ADD` is re-exported for LDAP attack modules.

## Control Flow
`initConnection()` opens an unauthenticated ldap3 `Connection`. `sendNegotiate()` parses the incoming NTLM type 1, optionally removes SIGN, ALWAYS_SIGN, and SEAL flags, performs Sicily package discovery, sends `SICILY_NEGOTIATE_NTLM`, and stores the challenge in `sessionData`. `sendAuth()` unwraps SPNEGO, optionally strips MIC, key exchange, version, sign, always-sign, and seal fields from the type 3 message, then sends `SICILY_RESPONSE_NTLM`. Successful bind marks the ldap3 connection as bound and refreshes server info.

## State and Persistence Behavior
The ldap3 connection lock and `sasl_in_progress` flag guard bind state. `negotiateMessage`, `authenticateMessageBlob`, and `sessionData['CHALLENGE_MESSAGE']` are retained for ldap3 callbacks and SOCKS/attack reuse. No filesystem persistence occurs.

## Dependencies and Integration Points
It depends on ldap3 `Server`, `Connection`, Sicily bind operations, Impacket NTLM structures, SPNEGO, nt status constants, and ntlmrelayx config flags `remove_mic` and `remove_sign_seal`.

## Risks and Edge Cases
This is intentionally "hacky" ldap3 integration. LDAP signing requirements produce stronger-auth errors unless LDAPS is used. Flag stripping can invalidate standard NTLM semantics except for specific vulnerabilities or nonstandard clients. Missing ldap3 versions exit the process.

## Test Signals
Cover LDAP and LDAPS binds, NTLM package discovery failure, signing-required rejection, MIC removal, sign/seal removal, SPNEGO unwrap, server-info refresh, and keepalive base search.

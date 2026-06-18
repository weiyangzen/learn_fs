# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/ldap.py

Purpose: implements LDAP SOCKS relay reuse for ntlmrelayx. It fakes the client-side LDAP NTLM bind sequence, maps the authenticating identity to a stored relayed LDAP session, and then passes allowed LDAP traffic between the SOCKS client and the real server.

Important APIs and control flow: `skipAuthentication()` loops over BER-decoded LDAP messages from `recv_ldap_msg()`. It answers anonymous/empty bind with success and matched DN `NTLM`, answers `sicilyNegotiate` with the saved `CHALLENGE_MESSAGE` after clearing NTLM sign/seal, and handles `sicilyResponse` by parsing `NTLMAuthChallengeResponse`, normalizing `DOMAIN/user`, looking up `activeRelays`, marking it in use, and sending a success `BindResponse`. Pre-auth `SearchRequest` for `supportedCapabilities` and `supportedSASLMechanisms` receives handcrafted AD-like results.

State and persistence: in-memory state includes `username`, `session`, and `activeRelays[username]['inUse']`. `tunnelConnection()` releases `inUse` after `passthrough_sockets()` returns. No disk persistence is used.

Dependencies and integration: depends on pyasn1, `impacket.ldap.ldapasn1`, `impacket.ntlm`, and `SocksRelay`. It integrates with LDAP protocol clients that store `session.socket` and NTLM challenge data.

Risks and test signals: `recv_ldap_msg()` uses packet-size-short-read as a message boundary heuristic, shared relay mutation is unsynchronized, StartTLS is blocked, and Unbind is dropped to preserve the relay. Tests should cover BER decoding, supportedCapabilities/SASL preauth searches, domain normalization fallback, in-use rejection, StartTLS closure, Unbind suppression, and relay release.

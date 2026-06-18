# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/mssqlrelayserver.py

## Purpose
`mssqlrelayserver.py` implements a fake MSSQL/TDS listener that captures SQL Server integrated-auth NTLM and relays it to configured ntlmrelayx targets. It supports classic TDS pre-login/login flows and TDS 8.0 TLS-from-start detection.

## Important APIs, Types, and Functions
`MSSQLRelayServer` wraps nested `MSSQLServer` and `MSSQLHandler`. The server builds a self-signed TLS context for TDS 8.0. The handler provides packet reassembly helpers, `sendNegotiate()`, `sendLoginFailed()`, `handle()`, and `do_attack()`.

## Control Flow
The handler chooses a target at connection start and parses target netloc. `handle()` peeks for TLS, wraps the socket when needed, then reassembles TDS messages. On pre-login it initializes the relay client and responds with encryption settings. On LOGIN7 it parses client login fields, rejects non-SSPI SQL auth, optionally overrides MSSQL target negotiation to preserve login/database semantics, relays type 1, and returns a TDS SSPI challenge token. On TDS SSPI it sends a local login failure to the client, relays type 3, logs success/failure, saves hash output, registers the target, and dispatches attack/SOCKS.

## State and Persistence Behavior
State includes selected target, `login` data, `tds8_mode`, `challengeMessage`, relay client, auth user, generated TLS context, and optional hash output file writes. Temporary cert/key material is written to a temp file then unlinked after loading.

## Dependencies and Integration Points
It depends on Impacket `tds`, NTLM, target parsing, active SOCKS connections, configured protocol clients/attacks, and `cryptography` for certificate creation.

## Risks and Edge Cases
TDS packet reassembly and TLS boundaries are easy to mishandle. Self-signed cert generation requires `cryptography`. SQL password logins are logged and rejected rather than relayed. The code sends login failed before processing relay success, which is intentional for capture flow but visible to clients.

## Test Signals
Cover TDS 7.x pre-login, TDS 8.0 TLS, fragmented packets, LOGIN7 with and without SSPI, database override, MSSQL-to-MSSQL relay, auth success/failure, hash output, and SOCKS/attack dispatch.

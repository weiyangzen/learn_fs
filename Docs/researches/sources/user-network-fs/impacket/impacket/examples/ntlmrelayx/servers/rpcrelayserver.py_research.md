# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/rpcrelayserver.py

## Purpose
`rpcrelayserver.py` implements a DCE/RPC listener that relays incoming RPC NTLM authentication to ntlmrelayx target clients. It also responds to endpoint mapper and IObjectExporter calls enough to keep RPC clients moving through authentication.

## Important APIs, Types, and Functions
`RPCRelayServer` wraps `RPCSocketServer` and `RPCHandler`. The handler uses `DCERPCServer`, callback handlers `handle_epmap()` and `send_ServerAlive2Response()`, request dispatch `handle_single_request()`, NTLM state machine `negotiate_ntlm_session()`, `bind()`, `send_error()`, `do_ntlm_negotiate()`, `do_ntlm_auth()`, and `do_attack()`.

## Control Flow
`setup()` registers EPM and IObjectExporter callbacks and creates reflection targets when needed. `handle()` receives RPC PDUs and delegates. BIND/ALTERCTX with WINNT auth enters NTLM negotiation: type 1 selects a target, initializes a protocol client, forwards negotiate, and returns a bind ack with challenge auth data; type 3 authenticates to the target, records hash material, registers target success, runs attack/SOCKS, and returns access denied to the RPC caller.

## State and Persistence Behavior
Per-connection fields cache request headers, PDU data, security trailers, challenge, target, client, and authenticated user. Successful relays may write hash output and queue active SOCKS sessions.

## Dependencies and Integration Points
It depends on Impacket DCE/RPC runtime, EPM/DCOM structures, NTLM constants, target processor, active SOCKS queue, configured protocol clients, and attack classes.

## Risks and Edge Cases
Only WINNT/default auth is implemented; SPNEGO, Kerberos, Schannel, Netlogon, and challenge-message handling are not. Bind accepts most context items to force authentication and rejects NDR64. It returns access denied after successful relay, which is expected but may affect client retry behavior.

## Test Signals
Test BIND without auth, WINNT type1/type3, unsupported auth types, endpoint mapper reflection, feature-negotiation context items, target reload, successful relay dispatch, and outputFile hash writing.

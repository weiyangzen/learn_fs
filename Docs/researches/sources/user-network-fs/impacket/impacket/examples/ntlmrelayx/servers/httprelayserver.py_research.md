# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/httprelayserver.py

## Purpose
`httprelayserver.py` implements the HTTP listener side of ntlmrelayx. It accepts browser/WebDAV/proxy NTLM authentication, relays it to configured protocol clients, supports multirelay redirection, serves WPAD/image responses, and dispatches attacks or SOCKS sessions after success.

## Important APIs, Types, and Functions
`HTTPRelayServer` is a thread wrapper around nested `HTTPServer` and `HTTPHandler`. The handler implements HTTP verbs, `strip_blob()`, `do_local_auth()`, `do_relay()`, `do_ntlm_negotiate()`, `do_ntlm_auth()`, `do_attack()`, WPAD/image helpers, redirects, and error responses.

## Control Flow
Requests flow through `do_GET()`, `do_POST()`, `do_CONNECT()`, or WebDAV `do_PROPFIND()`. The handler extracts NTLM from Authorization or Proxy-Authorization headers. In multirelay mode it first performs local auth to identify the user, selects a target for that identity, and redirects the client to force a new auth. Relay mode initializes the protocol client, forwards type 1, sends the target challenge to the HTTP client, forwards type 3, records John-the-Ripper hash material, registers target status, then starts an attack thread or queues a SOCKS connection.

## State and Persistence Behavior
Per-request state includes `target`, `client`, `challengeMessage`, `authUser`, and `relayToHost`. Server state includes config and `wpad_counters`. It may write hash output through `writeJohnOutputToFile`; otherwise it queues live sessions into `activeConnections`.

## Dependencies and Integration Points
It depends on `http.server`, `socketserver`, Impacket NTLM, SMB hash-output helpers, `TargetsProcessor`, `activeConnections`, configured protocol clients, attacks, and SOCKS server capabilities.

## Risks and Edge Cases
Header parsing is NTLM-only and assumes base64 tokens. Multirelay relies on browser redirect/retry behavior. `send_error()` checks `message.find('RPC_IN')` without comparing to `>= 0`, which is always truthy for `-1`. WPAD counters control when PAC files are served and can be sensitive to client retry behavior.

## Test Signals
Test direct, proxy, CONNECT, WebDAV PROPFIND, WPAD, redirect mode, disableMulti mode, target exhaustion, remove_target AV-pair stripping, hash dump output, SOCKS queuing, and attack fallback.

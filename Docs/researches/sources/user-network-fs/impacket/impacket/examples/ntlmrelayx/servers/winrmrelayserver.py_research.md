# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/winrmrelayserver.py

Purpose: implements the HTTP WinRM relay frontend on port 5985 by default. It handles `/wsman` NTLM/Negotiate authentication, WebDAV-style methods used for coercion, multirelay redirects, optional WPAD/image responses, and dispatches successful relays to SOCKS or attack modules.

Important APIs and control flow: `HTTPHandler` overrides HTTP verbs. `do_GETPOST()` only relays POSTs to `/wsman`; other paths get 404 plus Negotiate. `strip_blob()` extracts NTLM tokens from authorization headers. `do_local_auth()` performs multirelay capture with a local challenge, stores `authUser`, chooses a target, and redirects. `do_relay()` handles NTLM type 1 by selecting/initializing a protocol client and returning the real challenge, and type 3 by sending auth to the target, writing John-format hashes, then calling `do_attack()` and either redirecting or returning terminal responses.

State and persistence: per-handler state tracks challenge, target, client, auth user, relay mode, and negotiation count. Server-level state has WPAD counters. Persistent side effects are optional output-file hash writes and target processor bookkeeping.

Dependencies and integration: depends on Python `http.server`, Impacket NTLM, `TargetsProcessor`, `activeConnections`, configured protocol clients, configured attacks, and `get_address()`.

Risks and test signals: `send_error()` uses `message.find('RPC_IN')` truthily, likely matching unexpectedly when `find()` returns `-1`. Token parsing assumes NTLMSSP layout once a header is present. Tests should cover unauthenticated WSMANIDENTIFY, `/wsman` body drain, proxy CONNECT, multirelay local auth and redirect, disableMulti behavior, negotiation count rejection, failed target rotation, SOCKS enqueue, hash output, PROPFIND multi-status, and serve-image fallback.

# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/clients/httprelayclient.py

## Purpose
`httprelayclient.py` provides HTTP and HTTPS relay target clients. It turns an incoming NTLM negotiate/authenticate exchange into `Authorization: NTLM` or `Authorization: Negotiate` requests against a web server and treats any non-401 final response as successful authentication.

## Important APIs, Types, and Functions
`HTTPRelayClient` implements `initConnection()`, `sendNegotiate()`, `sendAuth()`, `killConnection()`, and `keepAlive()`. `HTTPSRelayClient` reuses all behavior but creates an `HTTPSConnection` with an SSL context. `PROTOCOL_CLIENT_CLASSES` registers both `HTTPRelayClient` and `HTTPSRelayClient`.

## Control Flow
`initConnection()` creates an HTTP connection and normalizes path/query. `sendNegotiate()` first probes the URL to obtain `WWW-Authenticate`, selects NTLM over Negotiate when both are offered, sends the base64 type 1 token, extracts a challenge from the response header, and returns `NTLMAuthChallenge`. `sendAuth()` unwraps SPNEGO responses, base64 encodes the NTLM token, sends another GET, and returns access denied only on HTTP 401. `keepAlive()` sends a HEAD request for `/favicon.ico`.

## State and Persistence Behavior
State lives in the connection object, `path`, `query`, `authenticationMethod`, and cached `lastresult` response body after a successful relay. No filesystem writes occur in this client.

## Dependencies and Integration Points
It uses Python `http.client`/`httplib`, `ssl`, `base64`, regex header parsing, Impacket NTLM/SPNEGO, and ntlmrelayx `ProtocolClient`. The HTTP relay server and SOCKS HTTP plugin can reuse the authenticated `HTTPConnection` session.

## Risks and Edge Cases
Header parsing assumes a single recognizable challenge in `WWW-Authenticate`. Non-401 status codes are considered success even if the target application denies access later. Anonymous ADCS/IIS handling can force NTLM despite missing auth headers. Keepalive ignores response state and may fail if a previous response body was not consumed.

## Test Signals
Exercise NTLM and Negotiate headers, query preservation, HTTPS context creation, 401 failure, 200/403/500 success semantics, missing headers, ADCS anonymous fallback, and SOCKS reuse of `lastresult`/socket state.

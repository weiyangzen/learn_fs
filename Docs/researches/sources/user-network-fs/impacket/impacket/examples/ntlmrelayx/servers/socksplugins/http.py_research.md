# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/http.py

## Purpose
`socksplugins/http.py` implements the HTTP SOCKS relay plugin. It lets a SOCKS client reuse a previously relayed HTTP session by authenticating to the local proxy with Basic credentials matching an active relay identity.

## Important APIs, Types, and Functions
`HTTPSocksRelay` extends `SocksRelay` and defines `PLUGIN_NAME`, `PLUGIN_SCHEME`, `getProtocolPort()`, `skipAuthentication()`, `getHeaders()`, `prepareRequest()`, `transferResponse()`, `transferChunked()`, and `tunnelConnection()`. `PLUGIN_CLASS` names the exported plugin class.

## Control Flow
`skipAuthentication()` reads the first HTTP request from the SOCKS socket, parses headers, requires `Authorization: Basic`, normalizes usernames including `user@fqdn` into `DOMAIN/user`, locates a matching idle active relay, binds `self.session` and `relaySocket` to the HTTPConnection socket, forwards the sanitized request, and relays the response. `tunnelConnection()` repeats request sanitization and response transfer for subsequent requests.

## State and Persistence Behavior
The plugin tracks `username`, `session`, `relaySocket`, and `packetSize`. It consumes active relay entries supplied by the SOCKS server but does not persist data. It rewrites Authorization and Connection headers in forwarded requests.

## Dependencies and Integration Points
It depends on `SocksRelay`, Impacket logging, and `activeRelays` entries containing `protocolClient.session`. It integrates directly with `HTTPRelayClient` sessions.

## Risks and Edge Cases
HTTP parsing is simple byte splitting and assumes complete headers in one recv. In `prepareRequest()`, comparing `part == ''` mixes bytes and str and may miss header termination. Chunked transfer parsing assumes chunk-size lines arrive cleanly.

## Test Signals
Test Basic auth prompt, username normalization, missing/active/in-use sessions, request body forwarding with Content-Length, connection header rewriting, no-body responses, content-length responses, chunked responses, and repeated tunnel requests.

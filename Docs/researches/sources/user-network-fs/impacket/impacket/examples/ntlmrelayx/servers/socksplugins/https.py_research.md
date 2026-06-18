# sources/user-network-fs/impacket/impacket/examples/ntlmrelayx/servers/socksplugins/https.py

## Purpose
`socksplugins/https.py` implements HTTPS SOCKS relay support by layering TLS server behavior over the HTTP SOCKS relay plugin. It lets local SOCKS users proxy HTTPS requests through relayed HTTPS target sessions.

## Important APIs, Types, and Functions
`HTTPSSocksRelay` subclasses `SSLServerMixin` and `HTTPSocksRelay`, sets `PLUGIN_NAME` to `HTTPS Socks Plugin`, `PLUGIN_SCHEME` to `HTTPS`, and overrides `getProtocolPort()` to return 443. It inherits authentication, request rewriting, response transfer, and tunneling from `HTTPSocksRelay`.

## Control Flow
Initialization calls `HTTPSocksRelay.__init__()` and creates an OpenSSL context through `SSLServerMixin`. The SOCKS server wraps client-side traffic in TLS, then the inherited HTTP plugin logic processes Basic auth, selects an active HTTPS relay, forwards sanitized HTTP requests over the already-authenticated target session, and relays responses.

## State and Persistence Behavior
State is inherited from `HTTPSocksRelay` plus TLS context/session state from `SSLServerMixin`. No files are written directly in this module; certificate behavior is delegated to the SSL utility mixin.

## Dependencies and Integration Points
It depends on OpenSSL, Impacket logging, `HTTPSocksRelay`, and `impacket.examples.ntlmrelayx.utils.ssl.SSLServerMixin`. Active relay entries are expected to come from HTTPS target clients.

## Risks and Edge Cases
TLS behavior depends entirely on the mixin and client trust of the generated certificate. HTTP parsing risks are inherited from `http.py`. The module imports `LOG` but does not use it, indicating minimal local logic.

## Test Signals
Test plugin discovery, default port 443, TLS handshake with SOCKS clients, Basic auth session selection, inherited content-length/chunked forwarding, certificate generation/trust failure handling, and HTTPS active relay reuse.

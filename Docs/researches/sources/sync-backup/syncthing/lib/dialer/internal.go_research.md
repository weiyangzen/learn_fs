## sources/sync-backup/syncthing/lib/dialer/internal.go

Purpose: Initializes proxy support and implements SOCKS/HTTP/HTTPS proxy dialing internals while preserving intended remote address semantics.

Important APIs/types/functions: Package init registers `socks`, `http`, and `https` proxy dialers and may replace `http.DefaultTransport`. `socksDialerFunction`, `httpDialerFunction`, `httpProxyDialer.DialContext`, `bufferedConn`, `dialerConn`, `newDialerAddr`, and `fallbackAddr` are key internals.

Control flow: Init reads proxy environment and `ALL_PROXY_NO_FALLBACK`, registers proxy dialer types, configures default HTTP transport through this package when a proxy is detected, and logs proxy state asynchronously. HTTP proxy dialing connects to proxy, optionally TLS-wraps HTTPS proxy, sends CONNECT with optional Basic auth, validates 200 OK, and returns a buffered connection preserving any bytes already read. Proxy connections are wrapped in `dialerConn` so `RemoteAddr` reports the target rather than the proxy.

State and persistence: Process-global proxy registration/default transport changes and `warnCleartextProxyAuthOnce`. No durable state.

Dependencies and integration points: Used by public dial functions and global discovery HTTP clients. Integrates with `golang.org/x/net/proxy` and `net/http`.

Risks: Global `http.DefaultTransport` mutation affects other package users. Cleartext proxy auth is security-sensitive but warns once. The target address fudge is required for LAN checks and relay logic; removing it would alter connection classification.

Test signals: No direct tests in this subset.

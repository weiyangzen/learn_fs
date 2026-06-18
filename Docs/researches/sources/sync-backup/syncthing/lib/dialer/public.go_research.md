## sources/sync-backup/syncthing/lib/dialer/public.go

Purpose: Public dialer helpers for TCP socket options, traffic class, proxy-aware dialing, reuse-port dialing, and racing fallback strategies.

Important APIs/types/functions: `SetTCPOptions`, `SetTrafficClass`, `DialContext`, `DialContextReusePortFunc`, and `dialTwicePreferFirst`; error `errUnexpectedInterfaceType`.

Control flow: TCP options set linger, Nagle/NoDelay, keepalive period, and keepalive. Traffic class sets IPv4 TOS and IPv6 traffic class. Proxy dialing chooses proxy direct/no-fallback/fallback paths. Reuse-port dialing skips local-address reuse when a proxy is configured, otherwise queries the connection registry for an unspecified TCP listen address and races reuse vs non-reuse dialing. `dialTwicePreferFirst` starts the preferred dial immediately and the fallback after a delay, returning first success preference and closing late fallback success.

State and persistence: Stateless except registry reads and proxy environment.

Dependencies and integration points: Core dependency for TCP transport and global announce client; uses `registry.Registry`, `ipv4`, `ipv6`, and `proxy`.

Risks: Racing dials must close losing connections to avoid leaks. Traffic class returns IPv4 error before IPv6 error, which may matter on dual-stack sockets. `SetTCPOptions` accepts only raw TCP or `dialerConn`.

Test signals: Only placeholder coverage in this package; behavior is mainly integration-tested through connections.

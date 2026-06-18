## sources/sync-backup/syncthing/lib/connections/tcp_dial.go

Purpose: Implements outbound TCP BEP dialing.

Important APIs/types/functions: Registers `tcp`, `tcp4`, and `tcp6` dialers. `tcpDialer.Dial` performs port fixup, registry-aware dialing, TCP option setup, traffic class setup, TLS client handshake, LAN/WAN priority calculation, and `internalConn` construction. `tcpDialerFactory` builds config-derived dialers.

Control flow: Dial wraps the context in a 10-second timeout, dials with `dialer.DialContextReusePortFunc`, applies socket options, wraps as TLS client, performs timed handshake, checks locality from the actual remote address, and returns a TCP client connection.

State and persistence: Transient socket/TLS state only. Registry may supply local listen address reuse.

Dependencies and integration points: Depends on dialer package, registry, config options, TLS config, and service dial loop.

Risks: Setting TCP options failure is logged but not fatal; TLS handshake failure closes the TLS connection. Reuse-port behavior varies by platform.

Test signals: Covered indirectly by TCP connection integration tests and dialer helper behavior.

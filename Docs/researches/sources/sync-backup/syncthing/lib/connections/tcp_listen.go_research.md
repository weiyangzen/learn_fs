## sources/sync-backup/syncthing/lib/connections/tcp_listen.go

Purpose: Implements TCP BEP listeners, NAT port mapping, LAN/WAN address advertisement, and accepted connection handoff.

Important APIs/types/functions: `tcpListener` implements `genericListener`; `serve` binds with reuse-port control, registers local address, creates NAT mapping, accepts TCP, performs TLS server handshake, computes priority, and sends `internalConn`. `WANAddresses` and `LANAddresses` expose mapped and local addresses. `tcpListenerFactory` creates listeners.

Control flow: Listener resolves and binds the configured address, replaces port zero with actual port for notifications, registers the listen address for outbound reuse, starts NAT mapping, and loops with one-second accept deadlines for cancellation responsiveness. Non-timeout accept failures back off and restart after a threshold. Accepted sockets get TCP options, optional traffic class, TLS handshake, and LAN/WAN priority before handoff.

State and persistence: Holds NAT mapping and actual local address behind mutex; registry entries live while serving. No persistent state.

Dependencies and integration points: Uses net listeners, dialer socket controls, NAT service, registry, config, `lanChecker`, and service listener supervisor.

Risks: Address advertisement must account for `:0`, unspecified binds, NAT mappings, and reuse-port punch-through zero-port announcements. Accept failure threshold controls listener restart behavior.

Test signals: Indirect connection establishment tests cover basic listener/dialer behavior.

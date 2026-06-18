## sources/sync-backup/syncthing/lib/connections/quic_listen.go

Purpose: Implements QUIC listeners, address advertisement, STUN/NAT detection, and accepted QUIC stream handoff.

Important APIs/types/functions: `quicListener` implements `genericListener` and STUN callbacks. `serve` binds UDP, creates a `quic.Transport`, starts STUN service over non-QUIC packets, registers the transport, listens for sessions, accepts a stream, and sends an `internalConn`. `WANAddresses`, `LANAddresses`, `NATType`, and callbacks expose dynamic addresses.

Control flow: Startup resolves and binds the listen address, starts STUN, registers transport for outbound reuse, starts QUIC listener, creates NAT mapping, records local address, then loops accepting sessions. Each accepted session must provide a stream within `quicOperationTimeout`; failures close the session and continue. Repeated accept errors restart via supervisor after threshold.

State and persistence: Holds current external STUN address, NAT type in `atomic.Uint64`, NAT mapping, local address, and mutex-protected address state. No durable state.

Dependencies and integration points: Integrates `quic-go`, `stun`, `nat.Service`, registry, `lanChecker`, event address notifier, and service listener supervision.

Risks: Concurrent address callbacks and listener teardown require careful locking. QUIC/STUN share one UDP socket through `transportPacketConn`; incorrect packet handling can break discovery or connectivity. NAT address changes must trigger notifications or discovery announcements become stale.

Test signals: No direct file tests; risks are covered indirectly by listener integration and platform network tests.

## sources/sync-backup/syncthing/lib/connections/quic_dial.go

Purpose: Implements QUIC outbound dialing when QUIC support is enabled.

Important APIs/types/functions: Registers `quic`, `quic4`, and `quic6` schemes in `init`. `quicDialer.Dial` resolves UDP addresses, chooses a reusable listener `*quic.Transport` from the registry when available, dials QUIC with TLS, opens a stream, computes LAN/WAN priority, and returns an `internalConn`. `quicDialerFactory` builds dialers from config priorities and reconnect interval.

Control flow: `Dial` default-fills missing ports, maps URL scheme to UDP network, resolves remote address, reuses a registered unspecified transport if possible, otherwise creates an ephemeral UDP packet conn, applies a 10-second operation timeout, dials, opens the first stream, and wraps the session/stream in `quicTlsConn`.

State and persistence: Uses transient QUIC sessions and optional ephemeral packet conns. Reused transports are held in the shared registry by listeners.

Dependencies and integration points: Depends on `quic-go`, `config`, `registry`, `protocol`, and common connection service dialer interfaces. Integrated through the package `dialers` map.

Risks: Resource cleanup is critical when dialing or opening the stream fails, especially for ephemeral packet conns. Reuse selection depends on registry predicate `transportConnUnspecified`.

Test signals: No direct tests in this file; coverage depends on connection integration tests and QUIC-enabled builds.

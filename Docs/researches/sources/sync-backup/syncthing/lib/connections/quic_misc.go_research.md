## sources/sync-backup/syncthing/lib/connections/quic_misc.go

Purpose: Provides shared QUIC configuration, URL-scheme network mapping, QUIC-to-TLS connection adapter, and packet-conn adapter for STUN over QUIC transport.

Important APIs/types/functions: `quicConfig` sets idle timeout and keepalive. `quicNetwork` maps `quic4`/`quic6` to UDP networks. `quicTlsConn` embeds `*quic.Conn` and `*quic.Stream` and implements `Close` and `ConnectionState`. `transportConnUnspecified` selects reusable unspecified transports. `transportPacketConn` adapts `quic.Transport` to `net.PacketConn`.

Control flow: `quicTlsConn.Close` closes stream, QUIC connection, and optional created packet conn, returning the first error. `transportPacketConn.ReadFrom` uses an optional stored read deadline to create a context and calls `ReadNonQUICPacket`; `WriteTo` forwards via transport.

State and persistence: Keeps optional created packet connection and atomic-value read deadline. No persistence.

Dependencies and integration points: Used by QUIC dial/listen, registry preferred transport selection, and STUN service.

Risks: Deadline handling is read-only and write deadline is ignored. Close ordering may surface only the first error. The adapter must remain compatible with `quic-go` non-QUIC packet APIs.

Test signals: No direct tests; exercised by QUIC listener/dialer runtime paths.

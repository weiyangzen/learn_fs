# sources/sync-backup/syncthing/cmd/strelaysrv/listener.go

Purpose: accepts relay protocol and session data connections, manages joined clients, and brokers session invitations.

Important APIs/state/functions: global `outboxes`, `outboxesMut`, `numConnections`; `listener`, `protocolConnectionHandler`, `sessionConnectionHandler`, and `messageReader`.

Control flow: `listener` accepts TCP with `tlsutil.DowngradingListener`, sets TCP options, and dispatches TLS protocol connections to `protocolConnectionHandler` and non-TLS session joins to `sessionConnectionHandler`. Protocol connections TLS-handshake with client certificates, derive device IDs, read relay protocol messages, handle joins, connect requests, pings, idle timeouts, over-limit refusal, duplicate IDs, and outbox invitations. Session connections read `JoinSessionRequest`, find a pending session by key, attach the connection, and return protocol responses.

State and persistence: joined clients are represented by per-device outbox channels in the global map. Sessions live in globals from `session.go`. No durable persistence exists.

Dependencies/integration: uses Syncthing relay protocol messages, Syncthing device IDs, TLS config from `main.go`, timeout globals, session creation, and limit monitoring.

Risks and test signals: connection handling is highly concurrent and relies on map locks and channel lifetimes. Closing outboxes during shutdown can interact with protocol handler sends. Over-limit handling drops idle joined clients with no active sessions. No direct tests in this subset cover protocol negotiation or session attach races.

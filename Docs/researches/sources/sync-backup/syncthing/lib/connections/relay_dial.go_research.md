## sources/sync-backup/syncthing/lib/connections/relay_dial.go

Purpose: Implements outbound connections through Syncthing relay servers.

Important APIs/types/functions: `relayDialer.Dial` obtains relay invitations and joins relay sessions. `relayDialerFactory` registers scheme `relay`, sets relay reconnect interval, and validates `RelaysEnabled`.

Control flow: Dial asks the relay for an invitation for the target device, joins the session, applies TCP options and traffic class, chooses TLS client/server mode based on invitation `ServerSocket`, performs timed TLS handshake, and returns a WAN relay `internalConn`.

State and persistence: No persistent state. Relay session and TLS connection are transient.

Dependencies and integration points: Uses relay `client`, dialer TCP helpers, config relay options, TLS certificates, and the common connection service dialer path.

Risks: Relay direction determines TLS role; wrong handling breaks handshakes. Relay is always WAN and does not allow separate LAN priority. Failure to set TCP options is fatal here while traffic class errors are debug-only.

Test signals: No direct tests; relay integration tests elsewhere must cover invitation/session paths.

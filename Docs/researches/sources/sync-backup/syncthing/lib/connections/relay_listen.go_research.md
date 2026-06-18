## sources/sync-backup/syncthing/lib/connections/relay_listen.go

Purpose: Implements relay listener clients that maintain relay-server connections and accept relay invitations as incoming Syncthing connections.

Important APIs/types/functions: Registers `relay`, `dynamic+http`, and `dynamic+https` listener schemes. `relayListener.serve` creates relay client and runs it. `handleInvitations` joins sessions, performs TLS, and emits `internalConn`. `WANAddresses`, `LANAddresses`, and `Error` expose relay client status.

Control flow: Listener creates a relay client, stores it under lock, starts invitation handling, and blocks in `clnt.Serve`. Invitation handling receives relay invitations, joins sessions, sets TCP options/traffic class, chooses TLS role from `ServerSocket`, handshakes, then sends a relay-server connection to the service. Every 10 seconds it detects dynamic relay URI changes and notifies address listeners.

State and persistence: Keeps current relay client behind a mutex and uses service error state. No durable state.

Dependencies and integration points: Integrates relay client library, service address-change notifications, config relay enablement, TLS config, and connection handoff channel.

Risks: Dynamic relay URI polling is coarse and pointer comparison can miss equal-value object changes unless client returns a distinct pointer. Relay client errors are surfaced through `Error`, so UI/API consumers depend on correct delegation.

Test signals: No direct tests in this file.

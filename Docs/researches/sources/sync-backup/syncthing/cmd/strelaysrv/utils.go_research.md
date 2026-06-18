# sources/sync-backup/syncthing/cmd/strelaysrv/utils.go

Purpose: applies TCP socket options for accepted relay connections.

Important APIs/functions: `setTCPOptions`.

Control flow: asserts the connection is a `*net.TCPConn`, then sets linger to zero, disables Nagle with `SetNoDelay(true)`, sets keepalive period to `networkTimeout`, and enables keepalive.

State and persistence: no persistent state; uses global `networkTimeout`.

Dependencies/integration: called by `listener` immediately after accepting TCP connections.

Risks and test signals: non-TCP connections return an error, but the caller ignores the result, so failed socket tuning does not reject clients. No direct tests cover socket option failures.

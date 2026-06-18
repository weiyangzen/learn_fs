# sources/sync-backup/syncthing/cmd/strelaysrv/session.go

Purpose: manages relay sessions between two devices and proxies bytes between their joined TCP connections.

Important APIs/state/functions: global `sessionMut`, `activeSessions`, `pendingSessions`, `numProxies`, `bytesProxied`; `newSession`, `findSession`, `dropSessions`, `hasSessions`, `session`, `AddConnection`, `Serve`, invitation builders, `CloseConns`, `proxy`, `makeRateLimitFunc`, and `take`.

Control flow: `newSession` generates two random 32-byte keys, creates optional per-session and global rate limiting behavior, and registers both keys as pending. `Serve` waits for two joined connections or times out, starts two proxy goroutines, records itself active, waits for either direction to finish, then removes pending/active entries and closes connections. `proxy` repeatedly reads with deadlines, increments byte counters, applies rate limiting, and writes to the peer with deadlines.

State and persistence: all session state is in memory. Pending sessions are keyed by raw key string, active sessions by slice membership, and counters are atomics.

Dependencies/integration: used by `listener.go` for connect and join flow, by `status.go` for reporting, and by rate limiter globals from `main.go`.

Risks and test signals: session keys are binary strings, which is valid for map keys but opaque in logs. `AddConnection` uses an unbuffered channel and fails if `Serve` is not actively selecting. Rate limiting reserves tokens on all limiters and sleeps the maximum delay. No direct tests here cover timeouts, cleanup, or proxy error races.

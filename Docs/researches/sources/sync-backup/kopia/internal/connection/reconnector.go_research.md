# sources/sync-backup/kopia/internal/connection/reconnector.go

Purpose: manages a single reusable connection and reconnects/retries operations when connector-specific closed-connection errors occur.

Important APIs/types/functions: `Connection`, `ConnectorImpl`, `Reconnector`, `GetOrOpenConnection`, generic `UsingConnection[T]`, `UsingConnectionNoResult`, `CloseActiveConnection`, and `NewReconnector`.

Control flow: `GetOrOpenConnection` lazily opens a connection under mutex and caches it. `UsingConnection` wraps open/callback execution in `retry.WithExponentialBackoff`, closes the active connection on open errors or callback errors classified by `IsConnectionClosedError`, and returns the callback result. `CloseActiveConnection` clears and closes the cached connection.

State and persistence behavior: state is only the in-memory active connection protected by a mutex. There is no pool, persistence, or per-operation lock around callback use.

Dependencies/integration: integrates with storage/provider connectors that implement closed-error classification, and with `retry` and Kopia logging.

Risks/test signals: callbacks can use the same connection concurrently because reuse is not serialized after retrieval. A connector must classify errors correctly or retries will not happen. Tests cover reuse, reconnect after closed errors, fatal open errors, nested use, close, and parallel callers.

# sources/sync-backup/syncthing/cmd/stdiscosrv/main.go

Purpose: main entrypoint and service wiring for the discovery server.

Important APIs/types/functions: constants for expiry, retry, HTTP timeouts, and replication outbox size; global `debug`; `CLI` flags/env bindings; and `main`.

Control flow: `main` parses Kong options, configures log level, handles `--version`, loads or generates TLS certificates unless HTTP proxy mode is enabled, creates the root Suture supervisor, optionally configures S3 blob storage, starts the in-memory database service, optionally starts AMQP replication, starts the API service, optionally starts a Prometheus metrics listener, and cancels the supervisor on SIGINT/SIGTERM after an optional shutdown delay.

State and persistence: delegates database persistence to `inMemoryStore`, certificates to configured cert/key files, optional S3 backups to blob storage, and optional AMQP replication to `amqp.go`.

Dependencies/integration: uses Kong, Suture, Syncthing build/tlsutil/protocol/rand helpers, Prometheus `promhttp`, S3 blob storage, and the API/database/metrics files in this package.

Risks and test signals: certificate auto-generation changes first-run behavior and device identity. HTTP mode trusts proxy-provided certificate and remote address headers. Metrics listener errors call `os.Exit(1)` from a goroutine. Tests are indirect through API and database test files.

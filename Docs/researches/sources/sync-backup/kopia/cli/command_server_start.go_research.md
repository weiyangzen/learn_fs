<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_start.go -->
# sources/sync-backup/kopia/cli/command_server_start.go

## Purpose
Implements `kopia server start`, including server option assembly, repository initialization, HTTP/GRPC routing, shutdown integration, authentication setup, Prometheus registration, UI/static serving, and optional KopiaUI notification output.

## Important APIs, Types, And Functions
Key symbols are `commandServerStart`, `setup`, `serverStartOptions`, `initRepositoryPossiblyAsync`, `run`, `setupHandlers`, `initPrometheus`, `stripProtocol`, and `getAuthenticator`. It feeds `server.Options`, uses `serverFlags`/`connectOptions`, and composes authenticators from htpasswd, one-shot passwords, server-control credentials, and repository user profiles.

## Control Flow
`setup` registers flags, then `run` validates insecure bind rules, builds `server.Options`, creates `server.Server`, initializes the repository synchronously or via retrying async mode, wires HTTP shutdown callbacks, creates a Gorilla router, optionally wraps it with GRPC routing, handles stdin-driven shutdown, registers SIGHUP refresh, and delegates serving to TLS/listener code.

## State And Persistence Behavior
Repository state is opened through the app service and installed into the server, then cleared on exit. It persists UI preferences path, auth cookie signing key, persistent log preference, scheduler/debug settings, and notification template settings through `server.Options`. Random passwords are intentionally process-local and printed to stderr only.

## Dependencies And Integration Points
Integrates `internal/server`, `internal/auth`, `insecureserverbind`, Gorilla mux, Prometheus `/metrics`, repository open/close services, notification senders, system signal reload hooks, and TLS serving from `command_server_tls.go`.

## Risks And Edge Cases
Security risk is concentrated around `--without-password`, `--insecure`, random credentials printed to stderr, and disabled CSRF checks. `io.ReadFull(rand.Reader, b)` ignores errors, so randomness failure is not surfaced. Shutdown paths must avoid deadlocking repository cleanup while HTTP/GRPC connections drain.

## Test Signals
Covered indirectly by CLI/server tests such as user-hash and terminate tests. High-value tests are insecure bind rejection, auth mode combinations, async repo connection retry, SIGHUP refresh, stdin shutdown, and server-control credentials.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_start.go -->

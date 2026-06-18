<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/servertesting/servertesting.go -->
# sources/sync-backup/kopia/internal/servertesting/servertesting.go

- Purpose: Supplies helpers for starting a Kopia server inside tests and connecting API-server-backed repositories.
- Important APIs/types/functions: `TestUsername`, `TestHostname`, `TestPassword`, `TestUIUsername`, `TestUIPassword`, `StartServer`, `StartServerContext`, `ConnectAndOpenAPIServer`.
- Control flow: `StartServerContext` builds a server with test authenticators, sets a repository, installs API/static handlers on a mux, starts an HTTP or TLS test server, and returns `APIServerInfo`. `ConnectAndOpenAPIServer` creates a temporary config, connects, registers cleanup, and opens the repo.
- State and persistence: Uses temporary config files, UI preferences files, test server lifecycle cleanup, and the provided repotesting repository.
- Dependencies and integration points: Integrates `auth`, `passwordpersist`, `repotesting`, `server`, `testlogging`, `testutil`, `repo`, and `content`.
- Risks and edge cases: TLS fingerprint calculation must match client trust behavior; cleanup order disconnects the repository before closing the server.
- Test signals: Used by `server_test.go` and other integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/servertesting/servertesting.go -->

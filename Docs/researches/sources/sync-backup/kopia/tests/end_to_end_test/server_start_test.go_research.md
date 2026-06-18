
# sources/sync-backup/kopia/tests/end_to_end_test/server_start_test.go

## Purpose
Exercises `kopia server start` behavior from the CLI and API client side. It covers authenticated TLS UI startup, server-control credentials, repository connect/create/disconnect via REST API, asynchronous repository connection, scheduler-driven snapshots and maintenance, insecure startup validation, and UI title escaping.

## Important APIs, Types, And Functions
- `TestServerStart` creates a filesystem repository, starts the server with UI/TLS/random passwords, authenticates both normal and server-control API clients, verifies throttling, source/snapshot listing, estimate tasks, upload/cancel APIs, object retrieval, and policy creation through `serverapi`.
- `TestServerStartAsyncRepoConnect` simulates an unavailable filesystem repository by renaming the repo path, verifies normal start failure, then verifies `--async-repo-connect` starts disconnected and later connects once the path returns.
- `TestServerCreateAndConnectViaAPI` and `TestConnectToExistingRepositoryViaAPI` exercise `CreateRepository`, `DisconnectFromRepository`, and `ConnectToRepository` request flows using `blob.ConnectionInfo` with filesystem options.
- `TestServerScheduling` validates server-side scheduling: per-source snapshot intervals and full maintenance scheduling run while the server process is alive.
- `TestServerStartInsecure`, `TestServerStartInsecureUnauthenticatedNonLoopbackRejected`, and `TestServerStartInsecureUnauthenticatedEscapeHatchNonLoopback` define the accepted and rejected insecure/unauthenticated bind combinations.
- Helpers include `verifyServerConnected`, `verifyUIServerConnected`, `waitForSnapshotCount`, `estimateSnapshotSize`, `uploadMatchingSnapshots`, `verifySnapshotCount`, `verifySourceCount`, `verifyUIServedWithCorrectTitle`, and `waitUntilServerStarted`.

## Control Flow
Tests build a `testenv.CLITest` with an in-process runner, run repository CLI setup, start the server with `RunAndProcessStderr`, parse `testutil.ServerParameters` from stderr, then use `apiclient.KopiaAPIClient` to issue `serverapi` calls. Long-running server commands return `wait` and sometimes `kill` callbacks; tests defer shutdown via `serverapi.Shutdown` or explicit process kill. Polling uses `retry.PeriodicallyNoValue` and direct sleep loops around status, task, and snapshot count endpoints.

## State And Persistence Behavior
The file mutates real temporary filesystem repositories, config state, snapshot manifests, policy manifests, maintenance schedules, throttling settings, and server runtime state. API create/connect tests persist repository configuration and verify connected/disconnected state transitions. Scheduling persists per-source policies and maintenance schedule state, then validates additional snapshot manifests and maintenance run records after server execution.

## Dependencies And Integration Points
Depends on `internal/apiclient`, `internal/serverapi`, `repo/blob/filesystem`, `snapshot/policy`, `maintenance`, `testenv`, `testutil.ServerParameters`, and shared test data directories. It bridges CLI process execution with HTTP API calls and UI HTML serving. Server-control authentication uses the constant username `server-control`.

## Risks And Edge Cases
The suite is timing-sensitive: server startup, async connect, estimate tasks, scheduled snapshots, and maintenance are all bounded by polling or sleeps. It depends on localhost bind behavior and on output parsing from server stderr. Security-sensitive cases assert unauthenticated insecure startup is limited to loopback unless a dangerous escape-hatch flag is provided. UI title verification protects HTML escaping of configured title prefixes.

## Test Signals
Strong integration signal for server lifecycle, API compatibility, repository creation/connect semantics, scheduling, security defaults, TLS fingerprint use, CSRF fetching, and UI title escaping. Failures often indicate cross-package regressions rather than isolated unit bugs.

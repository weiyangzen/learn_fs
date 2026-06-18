# sources/sync-backup/kopia/tests/end_to_end_test/server_repo_logs_test.go

## Purpose
Tests that server diagnostic/log blobs are uploaded to the repository when the server exits.

## Important APIs, Types, and Functions
`TestServerRepoLogsUploadedOnShutdown` uses `apiclient.NewKopiaAPIClient`, `serverapi.Status`, `FetchCSRFTokenForTesting`, `CreateSnapshotSource`, and `serverapi.Shutdown`.

## Control Flow
The test creates a repo, verifies repo creation uploaded one log, starts an insecure passwordless server, builds a control API client, waits until status is usable, fetches CSRF token, creates a snapshot source through server control API without taking a snapshot, checks server status, deletes existing logs with `logs cleanup --max-age=1ns`, verifies logs are empty, shuts the server down, waits for exit, and verifies logs list is non-empty.

## State and Persistence Behavior
Persists repository logs, server snapshot-source configuration, and server shutdown log upload. The test deliberately cleans existing logs to isolate shutdown behavior.

## Dependencies and Integration Points
Exercises server startup, control API auth/password generation, CSRF token handling, policy payloads, logs list/cleanup, and graceful shutdown.

## Risks
Startup polling treats some HTTP errors as not-started and others as started; unusual failures could pass the poll then fail later. Log upload timing is tied to graceful shutdown.

## Test Signals
Confirms server creates repository log artifacts on exit after prior logs were removed.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_status.go -->
# sources/sync-backup/kopia/cli/command_server_status.go

## Purpose
Implements `kopia server status`, a server-client command that lists sources currently known by a running server control API.

## Important APIs, Types, And Functions
Defines `commandServerStatus` with `serverClientFlags`, text output, and a `remote` filter flag. `runServerStatus` calls `KopiaAPIClient.Get` on `control/sources` and decodes `serverapi.SourcesResponse`.

## Control Flow
The command is registered under `server status`. At execution it connects via server action plumbing, requests source status, filters out entries marked `REMOTE` unless `--remote` was provided, and prints status/source pairs.

## State And Persistence Behavior
It does not mutate repository state. It observes transient server-side source status returned by the control endpoint.

## Dependencies And Integration Points
Depends on `internal/apiclient`, `internal/serverapi`, server authentication flags, and the server control API registered by `command_server_start.go`.

## Risks And Edge Cases
The string comparison to `REMOTE` is a loose contract with server API status values. Network/auth errors are wrapped as list failures, and output order is whatever the server returns.

## Test Signals
Useful signals are server integration tests that start a server, register local and remote sources, and verify `--remote` changes filtering without altering API requests.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_status.go -->

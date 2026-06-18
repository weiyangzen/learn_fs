<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle_get.go -->
# sources/sync-backup/kopia/cli/command_server_throttle_get.go

## Purpose
Implements `kopia server throttle get`, which reads throttling limits from a running server and emits either human-readable text or JSON.

## Important APIs, Types, And Functions
Defines `commandServerThrottleGet`, embeds `serverClientFlags`, and reuses `commonThrottleGet`. `run` uses `KopiaAPIClient.Get` against `control/throttle` into `throttling.Limits`.

## Control Flow
After server-action connection, it performs one GET request, then delegates formatting to `commonThrottleGet.output`.

## State And Persistence Behavior
No persistent state is changed. It reads the server's current in-memory or repository-backed throttling limits as exposed by control API.

## Dependencies And Integration Points
Depends on `internal/apiclient`, `repo/blob/throttling`, server client flag plumbing, and common output helpers.

## Risks And Edge Cases
Failure modes are network/auth/API errors and stale assumptions about the `control/throttle` payload shape. JSON output depends on `throttling.Limits` tags.

## Test Signals
Tests should exercise JSON and text output for unlimited and finite limits, plus server API failure wrapping.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle_get.go -->

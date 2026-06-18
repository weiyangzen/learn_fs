<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle_set.go -->
# sources/sync-backup/kopia/cli/command_server_throttle_set.go

## Purpose
Implements `kopia server throttle set`, allowing runtime modification of a running server's throttling limits.

## Important APIs, Types, And Functions
Defines `commandServerThrottleSet`, `serverClientFlags`, and `commonThrottleSet`. `run` GETs current `throttling.Limits`, applies CLI-specified changes, then PUTs to `control/throttle` with `serverapi.Empty` response.

## Control Flow
The command reads current limits first so unspecified flags are preserved. If `commonThrottleSet.apply` reports zero changes, it logs `No changes made` and skips the PUT. Otherwise it sends the changed limits to the server.

## State And Persistence Behavior
Mutates server-side throttle state through the control API. The file itself stores only parsed flag strings and a temporary change count.

## Dependencies And Integration Points
Depends on the shared throttle parser, `internal/apiclient`, `internal/serverapi`, and the server control endpoint.

## Risks And Edge Cases
String parsing accepts any float or int without local nonnegative validation, so backend enforcement matters. Partial update is all-or-nothing at API level, but concurrent writers can race because the command uses read-modify-write.

## Test Signals
Useful tests cover individual fields, `unlimited`/`-`, no-change behavior, parse errors, and preservation of unrelated existing limits.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle_set.go -->

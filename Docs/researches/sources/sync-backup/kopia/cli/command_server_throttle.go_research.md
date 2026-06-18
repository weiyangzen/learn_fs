<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle.go -->
# sources/sync-backup/kopia/cli/command_server_throttle.go

## Purpose
Provides the parent `kopia server throttle` command and groups runtime throttle inspection and mutation subcommands for a running server.

## Important APIs, Types, And Functions
Defines `commandServerThrottle` with `get` and `set` subcommands. Its only method, `setup`, creates the parent command and delegates setup to `commandServerThrottleGet` and `commandServerThrottleSet`.

## Control Flow
There is no command body beyond registration. Control flow enters the get or set child command after kingpin parses the selected subcommand.

## State And Persistence Behavior
This file has no state of its own. Runtime throttle state lives in the server and is fetched or updated by the child command implementations.

## Dependencies And Integration Points
Integrates with `command_server_throttle_get.go`, `command_server_throttle_set.go`, and shared throttle formatting/parsing helpers in `throttle_get.go` and `throttle_set.go`.

## Risks And Edge Cases
The main risk is only command-surface drift: if a child command changes names or flags, this parent must still register them in the intended CLI tree.

## Test Signals
Test signals should verify command discovery/help and that both child commands are reachable through the `server throttle` namespace.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/command_server_throttle.go -->

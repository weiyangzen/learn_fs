<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_test.go -->
# sources/user-network-fs/rclone/fs/config_test.go

## Purpose
Tests context-scoped global `fs.ConfigInfo` behavior and RC request context propagation.

## Important APIs, Types, And Control Flow
`TestGetConfig` checks nil context fallback, default global config, `AddConfig` shallow copy behavior, and retrieving context-local config. `TestRCRequestContext` verifies `WithRCRequest`, `IsRCRequest`, and `CopyConfig` preserve or omit the marker correctly with and without an embedded config.

## State And Persistence
No persistent state. Contexts carry copied config and marker values; one context-local config mutates `Transfers` to prove independence.

## Dependencies And Integration Points
Targets package `fs` configuration context helpers, which are consumed across command, RC, and backend code.

## Risks And Test Signals
Good regression signal for detached RC contexts. It does not deeply test every `ConfigInfo` field copied by `AddConfig`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/config_test.go -->

# sources/sync-backup/kopia/tests/compat_test/compat_test.go

## Purpose
Black-box compatibility tests across historical Kopia binaries and the current binary.

## Important APIs, Types, and Functions
Global environment-derived binary paths are `KOPIA_CURRENT_EXE`, `KOPIA_08_EXE`, and `KOPIA_017_EXE`. Tests use `testenv.NewExeRunnerWithBinary` and `NewCLITest`.

## Control Flow
Tests create repositories or server configs with old/current binaries, switch runners, connect, list snapshots, perform upgrades, and assert expected success/failure. The v0.17 server test starts an old server, connects an old client, then switches that client config to the current binary.

## State and Persistence Behavior
Creates real filesystem repositories, client configs, format cache files, server TLS files, and server user records. Upgrade tests mutate repository format state and poison old-client access.

## Dependencies and Integration Points
Exercises CLI repo create/connect/status/upgrade, snapshot commands, server start/users, TLS fingerprint handling, old format cache refresh, and persisted client config compatibility.

## Risks
Tests skip when required binary env vars are absent, so coverage depends on CI setup. They rely on old executable behavior and text output stability. Time sleeps guard cache mtime checks and server startup.

## Test Signals
Signals include current opening v0.8 repos, v0.8 opening current format v1 repos, v0.8 rejection of default current/v2 repos, cache refresh throttling, upgrade lock behavior, and current client compatibility with v0.17 server config.

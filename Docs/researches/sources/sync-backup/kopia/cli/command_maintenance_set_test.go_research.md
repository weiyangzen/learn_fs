# sources/sync-backup/kopia/cli/command_maintenance_set_test.go

## Purpose
Test coverage for `command_maintenance_set` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestMaintenanceSetExtendObjectLocks, TestMaintenanceSetListParallelism.

## APIs, Types, and Functions
Important APIs include functions/methods `TestMaintenanceSetExtendObjectLocks`, `TestMaintenanceSetListParallelism`, `TestInvalidExtendRetainOptions`; tests TestMaintenanceSetExtendObjectLocks, TestMaintenanceSetListParallelism.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches maintenance params, schedule, and maintenance statistics, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports testing, time, github.com/stretchr/testify/require, github.com/kopia/kopia/cli, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/repo/blob, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/cli, kopia/internal/testutil, kopia/repo/blob, kopia/tests/testenv plus external packages testing, time, github.com/stretchr/testify/require.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. test signals come from named tests TestMaintenanceSetExtendObjectLocks, TestMaintenanceSetListParallelism.

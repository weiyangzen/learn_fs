# sources/sync-backup/kopia/cli/command_maintenance_info_test.go

## Purpose
Test coverage for `command_maintenance_info` CLI behavior. It exercises command execution through the Kopia test environment and asserts output, repository state, and error handling for TestMaintenanceInfoSimple.

## APIs, Types, and Functions
Important APIs include functions/methods `TestMaintenanceInfoSimple`; tests TestMaintenanceInfoSimple.

## Control Flow, State, and Persistence
Control flow registers a namespace or shared helper used by sibling commands, then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches maintenance params, schedule, and maintenance statistics, temporary test repositories and captured CLI output. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports testing, github.com/kopia/kopia/cli, github.com/kopia/kopia/internal/testutil, github.com/kopia/kopia/tests/testenv. It integrates with Kopia repository internals such as kopia/cli, kopia/internal/testutil, kopia/tests/testenv plus external packages testing.

## Risks and Test Signals
Risks and test signals: test signals come from named tests TestMaintenanceInfoSimple.

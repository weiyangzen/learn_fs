# sources/sync-backup/kopia/cli/command_logs.go

## Purpose
Command group root for encrypted repository log browsing and cleanup. It registers list/show/cleanup commands.

## APIs, Types, and Functions
Important APIs include types `commandLogs`; functions/methods `setup`; Kingpin command(s) logs: Commands to manipulate logs stored in the repository..

## Control Flow, State, and Persistence
Control flow registers command(s) logs: Commands to manipulate logs stored in the repository., then runs through a test/helper flow. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: depends on sibling CLI command registration and shared app service interfaces in the `cli` package.

## Risks and Test Signals
Risks and test signals: main risks are flag validation drift, repository access-mode mismatch, and insufficient coverage of error paths. nearby test file `sources/sync-backup/kopia/cli/command_logs_test.go` provides direct coverage.

# sources/sync-backup/kopia/cli/command_maintenance_set.go

## Purpose
Maintenance parameter update command for owner, quick/full enablement, intervals, pauses, log retention, object-lock extension, and blob-list parallelism.

## APIs, Types, and Functions
Important APIs include types `commandMaintenanceSet`; functions/methods `setup`, `setLogCleanupParametersFromFlags`, `setListBlobsParallelismFromFlags`, `setMaintenanceOwnerFromFlags`, `setMaintenanceEnabledAndIntervalFromFlags`, `setMaintenanceObjectLockExtendFromFlags`, `run`; Kingpin command(s) set: Set maintenance parameters; flags owner: Set maintenance owner user@hostname, enable-quick: Enable or disable quick maintenance, enable-full: Enable or disable full maintenance, quick-interval: Set quick maintenance interval, full-interval: Set full maintenance interval, pause-quick: Pause quick maintenance for a specified duration, pause-full: Pause full maintenance for a specified duration, max-retained-log-count: Set maximum number of log sessions to retain, max-retained-log-age: Set maximum age of log sessions to retain, max-retained-log-size-mb: Set maximum total size of log sessions, plus 2 more.

## Control Flow, State, and Persistence
Control flow registers command(s) set: Set maintenance parameters, binds flags owner: Set maintenance owner user@hostname, enable-quick: Enable or disable quick maintenance, enable-full: Enable or disable full maintenance, quick-interval: Set quick maintenance interval, full-interval: Set full maintenance interval, pause-quick: Pause quick maintenance for a specified duration, pause-full: Pause full maintenance for a specified duration, max-retained-log-count: Set maximum number of log sessions to retain, plus 4 more, then runs through a direct repository write action. The implementation iterates blob storage, persists maintenance parameters, persists maintenance schedule. State and persistence: touches maintenance params, schedule, and maintenance statistics, encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, time, github.com/pkg/errors, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/maintenance. It integrates with Kopia repository internals such as kopia/internal/units, kopia/repo, kopia/repo/maintenance plus external packages context, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. nearby test file `sources/sync-backup/kopia/cli/command_maintenance_set_test.go` provides direct coverage.

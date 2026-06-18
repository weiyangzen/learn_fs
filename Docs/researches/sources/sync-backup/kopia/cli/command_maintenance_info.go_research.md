# sources/sync-backup/kopia/cli/command_maintenance_info.go

## Purpose
Maintenance information command that reads maintenance params, schedule, owner, and cycle statistics and prints quick/full maintenance status with human-readable messages.

## APIs, Types, and Functions
Important APIs include types `commandMaintenanceInfo`, `MaintenanceInfo`; functions/methods `setup`, `run`, `displayCycleInfo`, `getMessageFromRun`; Kingpin command(s) info: Display maintenance information.

## Control Flow, State, and Persistence
Control flow registers command(s) info: Display maintenance information, then runs through a direct repository read action. The main behavior is delegated through the functions declared in this file and shared Kopia repository APIs. State and persistence: touches maintenance params, schedule, and maintenance statistics, encrypted repository log blobs. Mutations go through Kopia repository/blob/config APIs rather than ad hoc file edits, except for explicitly offline shard-layout changes and cache-directory cleanup where applicable.

## Dependencies and Integration
Dependencies and integration: imports context, strings, time, github.com/pkg/errors, github.com/kopia/kopia/internal/clock, github.com/kopia/kopia/internal/units, github.com/kopia/kopia/repo, github.com/kopia/kopia/repo/maintenance, github.com/kopia/kopia/repo/maintenancestats. It integrates with Kopia repository internals such as kopia/internal/clock, kopia/internal/units, kopia/repo, kopia/repo/maintenance, kopia/repo/maintenancestats plus external packages context, strings, time, github.com/pkg/errors.

## Risks and Test Signals
Risks and test signals: parallel scans need cancellation, progress, and error propagation coverage. time/progress estimates are useful signals but can be flaky if asserted too tightly. nearby test file `sources/sync-backup/kopia/cli/command_maintenance_info_test.go` provides direct coverage.
